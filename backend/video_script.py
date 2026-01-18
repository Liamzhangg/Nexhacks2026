import os
import random
import sys
import json
import argparse
import contextlib
from typing import Sequence, Mapping, Any, Union
import torch


def get_value_at_index(obj: Union[Sequence, Mapping], index: int) -> Any:
    """Returns the value at the given index of a sequence or mapping.

    If the object is a sequence (like list or string), returns the value at the given index.
    If the object is a mapping (like a dictionary), returns the value at the index-th key.

    Some return a dictionary, in these cases, we look for the "results" key

    Args:
        obj (Union[Sequence, Mapping]): The object to retrieve the value from.
        index (int): The index of the value to retrieve.

    Returns:
        Any: The value at the given index.

    Raises:
        IndexError: If the index is out of bounds for the object and the object is not a mapping.
    """
    try:
        return obj[index]
    except KeyError:
        return obj["result"][index]


def find_path(name: str, path: str = None) -> str:
    """
    Recursively looks at parent folders starting from the given path until it finds the given name.
    Returns the path as a Path object if found, or None otherwise.
    """
    # If no path is given, use the current working directory
    if path is None:
        if args is None or args.comfyui_directory is None:
            path = os.getcwd()
        else:
            path = args.comfyui_directory

    # Check if the current directory contains the name
    if name in os.listdir(path):
        path_name = os.path.join(path, name)
        print(f"{name} found: {path_name}")
        return path_name

    # Get the parent directory
    parent_directory = os.path.dirname(path)

    # If the parent directory is the same as the current directory, we've reached the root and stop the search
    if parent_directory == path:
        return None

    # Recursively call the function with the parent directory
    return find_path(name, parent_directory)


def add_comfyui_directory_to_sys_path() -> None:
    """
    Add 'ComfyUI' to the sys.path
    """
    comfyui_path = find_path("ComfyUI")
    if comfyui_path is not None and os.path.isdir(comfyui_path):
        sys.path.append(comfyui_path)

        manager_path = os.path.join(
            comfyui_path, "custom_nodes", "ComfyUI-Manager", "glob"
        )

        if os.path.isdir(manager_path) and os.listdir(manager_path):
            sys.path.append(manager_path)
            global has_manager
            has_manager = True

        import __main__

        if getattr(__main__, "__file__", None) is None:
            __main__.__file__ = os.path.join(comfyui_path, "main.py")

        print(f"'{comfyui_path}' added to sys.path")


def add_extra_model_paths() -> None:
    """
    Parse the optional extra_model_paths.yaml file and add the parsed paths to the sys.path.
    """
    from comfy.options import enable_args_parsing

    enable_args_parsing()
    from utils.extra_config import load_extra_path_config

    extra_model_paths = find_path("extra_model_paths.yaml")

    if extra_model_paths is not None:
        load_extra_path_config(extra_model_paths)
    else:
        print("Could not find the extra_model_paths config file.")


def import_custom_nodes() -> None:
    """Find all custom nodes in the custom_nodes folder and add those node objects to NODE_CLASS_MAPPINGS

    This function sets up a new asyncio event loop, initializes the PromptServer,
    creates a PromptQueue, and initializes the custom nodes.
    """
    if has_manager:
        try:
            import manager_core as manager
        except ImportError:
            print("Could not import manager_core, proceeding without it.")
            return
        else:
            if hasattr(manager, "get_config"):
                print("Patching manager_core.get_config to enforce offline mode.")
                try:
                    get_config = manager.get_config

                    def _get_config(*args, **kwargs):
                        config = get_config(*args, **kwargs)
                        config["network_mode"] = "offline"
                        return config

                    manager.get_config = _get_config
                except Exception as e:
                    print("Failed to patch manager_core.get_config:", e)

    import asyncio
    import execution
    from nodes import init_extra_nodes
    import server

    # Creating a new event loop and setting it as the default loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def inner():
        # Creating an instance of PromptServer with the loop
        server_instance = server.PromptServer(loop)
        execution.PromptQueue(server_instance)

        # Initializing custom nodes
        await init_extra_nodes(init_custom_nodes=True)

    loop.run_until_complete(inner())


def save_image_wrapper(context, cls):
    if args.output is None:
        return cls

    from PIL import Image, ImageOps, ImageSequence
    from PIL.PngImagePlugin import PngInfo

    import numpy as np

    class WrappedSaveImage(cls):
        counter = 0

        def save_images(
            self, images, filename_prefix="ComfyUI", prompt=None, extra_pnginfo=None
        ):
            if args.output is None:
                return super().save_images(
                    images, filename_prefix, prompt, extra_pnginfo
                )
            else:
                if len(images) > 1 and args.output == "-":
                    raise ValueError("Cannot save multiple images to stdout")
                filename_prefix += self.prefix_append

                results = list()
                for batch_number, image in enumerate(images):
                    i = 255.0 * image.cpu().numpy()
                    img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
                    metadata = None
                    if not args.disable_metadata:
                        metadata = PngInfo()
                        if prompt is not None:
                            metadata.add_text("prompt", json.dumps(prompt))
                        if extra_pnginfo is not None:
                            for x in extra_pnginfo:
                                metadata.add_text(x, json.dumps(extra_pnginfo[x]))

                    if args.output == "-":
                        # Hack to briefly restore stdout
                        if context is not None:
                            context.__exit__(None, None, None)
                        try:
                            img.save(
                                sys.stdout.buffer,
                                format="png",
                                pnginfo=metadata,
                                compress_level=self.compress_level,
                            )
                        finally:
                            if context is not None:
                                context.__enter__()
                    else:
                        subfolder = ""
                        if len(images) == 1:
                            if os.path.isdir(args.output):
                                subfolder = args.output
                                file = "output.png"
                            else:
                                subfolder, file = os.path.split(args.output)
                                if subfolder == "":
                                    subfolder = os.getcwd()
                        else:
                            if os.path.isdir(args.output):
                                subfolder = args.output
                                file = filename_prefix
                            else:
                                subfolder, file = os.path.split(args.output)

                            if subfolder == "":
                                subfolder = os.getcwd()

                            files = os.listdir(subfolder)
                            file_pattern = file
                            while True:
                                filename_with_batch_num = file_pattern.replace(
                                    "%batch_num%", str(batch_number)
                                )
                                file = (
                                    f"{filename_with_batch_num}_{self.counter:05}.png"
                                )
                                self.counter += 1

                                if file not in files:
                                    break

                        img.save(
                            os.path.join(subfolder, file),
                            pnginfo=metadata,
                            compress_level=self.compress_level,
                        )
                        print("Saved image to", os.path.join(subfolder, file))
                        results.append(
                            {
                                "filename": file,
                                "subfolder": subfolder,
                                "type": self.type,
                            }
                        )

                return {"ui": {"images": results}}

    return WrappedSaveImage


def parse_arg(s: Any, default: Any = None) -> Any:
    """Parses a JSON string, returning it unchanged if the parsing fails."""
    if __name__ == "__main__" or not isinstance(s, str):
        return s

    try:
        return json.loads(s)
    except json.JSONDecodeError:
        return s


parser = argparse.ArgumentParser(
    description="A converted ComfyUI workflow. Node inputs listed below. Values passed should be valid JSON (assumes string if not valid JSON)."
)
parser.add_argument(
    "--unet_name1",
    default="wan2.1_vace_14B_fp16.safetensors",
    help='Argument 0, input `unet_name` for node "Load Diffusion Model" id 10 (autogenerated)',
)

parser.add_argument(
    "--weight_dtype2",
    default="fp8_e4m3fn_fast",
    help='Argument 1, input `weight_dtype` for node "Load Diffusion Model" id 10 (autogenerated)',
)

parser.add_argument(
    "--lora_name3",
    default="Wan21_CausVid_14B_T2V_lora_rank32.safetensors",
    help='Argument 1, input `lora_name` for node "LoraLoaderModelOnly" id 11 (autogenerated)',
)

parser.add_argument(
    "--strength_model4",
    default=0.30000000000000004,
    help='Argument 2, input `strength_model` for node "LoraLoaderModelOnly" id 11 (autogenerated)',
)

parser.add_argument(
    "--clip_name5",
    default="umt5_xxl_fp8_e4m3fn_scaled.safetensors",
    help='Argument 0, input `clip_name` for node "Load CLIP" id 12 (autogenerated)',
)

parser.add_argument(
    "--type6",
    default="wan",
    help='Argument 1, input `type` for node "Load CLIP" id 12 (autogenerated)',
)

parser.add_argument(
    "--vae_name7",
    default="wan_2.1_vae.safetensors",
    help='Argument 0, input `vae_name` for node "Load VAE" id 13 (autogenerated)',
)

parser.add_argument(
    "--text8",
    default="three pepsi cans spinning from above",
    help='Argument 0, input `text` for node "CLIP Text Encode (Positive Prompt)" id 24 (autogenerated)',
)

parser.add_argument(
    "--video9",
    default="4465010-hd_1920_1080_30fps.mp4",
    help='Argument 0, input `video` for node "Load Video (Upload) 🎥🅥🅗🅢" id 26 (autogenerated)',
)

parser.add_argument(
    "--force_rate10",
    default=0,
    help='Argument 1, input `force_rate` for node "Load Video (Upload) 🎥🅥🅗🅢" id 26 (autogenerated)',
)

parser.add_argument(
    "--custom_width11",
    default=720,
    help='Argument 2, input `custom_width` for node "Load Video (Upload) 🎥🅥🅗🅢" id 26 (autogenerated)',
)

parser.add_argument(
    "--custom_height12",
    default=720,
    help='Argument 3, input `custom_height` for node "Load Video (Upload) 🎥🅥🅗🅢" id 26 (autogenerated)',
)

parser.add_argument(
    "--frame_load_cap13",
    default=41,
    help='Argument 4, input `frame_load_cap` for node "Load Video (Upload) 🎥🅥🅗🅢" id 26 (autogenerated)',
)

parser.add_argument(
    "--skip_first_frames14",
    default=0,
    help='Argument 5, input `skip_first_frames` for node "Load Video (Upload) 🎥🅥🅗🅢" id 26 (autogenerated)',
)

parser.add_argument(
    "--select_every_nth15",
    default=1,
    help='Argument 6, input `select_every_nth` for node "Load Video (Upload) 🎥🅥🅗🅢" id 26 (autogenerated)',
)

parser.add_argument(
    "--text16",
    default="black background, mask, blurry, unrealistic, poor quality, animated, poorly drawn",
    help='Argument 0, input `text` for node "CLIP Text Encode (Negative Prompt)" id 30 (autogenerated)',
)

parser.add_argument(
    "--image17",
    default="300Wx300H-1-HYK-24769.jpg",
    help='Argument 0, input `image` for node "Load Image" id 32 (autogenerated)',
)

parser.add_argument(
    "--prompt18",
    default="coke bottle",
    help='Argument 1, input `prompt` for node "SAM3 Segmentation" id 28 (autogenerated)',
)

parser.add_argument(
    "--threshold19",
    default=0.4,
    help='Argument 2, input `threshold` for node "SAM3 Segmentation" id 28 (autogenerated)',
)

parser.add_argument(
    "--min_width_pixels20",
    default=0,
    help='Argument 3, input `min_width_pixels` for node "SAM3 Segmentation" id 28 (autogenerated)',
)

parser.add_argument(
    "--min_height_pixels21",
    default=0,
    help='Argument 4, input `min_height_pixels` for node "SAM3 Segmentation" id 28 (autogenerated)',
)

parser.add_argument(
    "--use_video_model22",
    default=True,
    help='Argument 5, input `use_video_model` for node "SAM3 Segmentation" id 28 (autogenerated)',
)

parser.add_argument(
    "--unload_after_run23",
    default=True,
    help='Argument 6, input `unload_after_run` for node "SAM3 Segmentation" id 28 (autogenerated)',
)

parser.add_argument(
    "--width24",
    default=720,
    help='Argument 3, input `width` for node "WanVaceToVideo" id 25 (autogenerated)',
)

parser.add_argument(
    "--height25",
    default=720,
    help='Argument 4, input `height` for node "WanVaceToVideo" id 25 (autogenerated)',
)

parser.add_argument(
    "--length26",
    default=41,
    help='Argument 5, input `length` for node "WanVaceToVideo" id 25 (autogenerated)',
)

parser.add_argument(
    "--batch_size27",
    default=1,
    help='Argument 6, input `batch_size` for node "WanVaceToVideo" id 25 (autogenerated)',
)

parser.add_argument(
    "--strength28",
    default=1,
    help='Argument 7, input `strength` for node "WanVaceToVideo" id 25 (autogenerated)',
)

parser.add_argument(
    "--shift29",
    default=8,
    help='Argument 1, input `shift` for node "ModelSamplingSD3" id 2 (autogenerated)',
)

parser.add_argument(
    "--seed30",
    default=812152535208420,
    help='Argument 1, input `seed` for node "KSampler" id 29 (autogenerated)',
)

parser.add_argument(
    "--steps31",
    default=4,
    help='Argument 2, input `steps` for node "KSampler" id 29 (autogenerated)',
)

parser.add_argument(
    "--cfg32",
    default=1,
    help='Argument 3, input `cfg` for node "KSampler" id 29 (autogenerated)',
)

parser.add_argument(
    "--sampler_name33",
    default="uni_pc",
    help='Argument 4, input `sampler_name` for node "KSampler" id 29 (autogenerated)',
)

parser.add_argument(
    "--scheduler34",
    default="simple",
    help='Argument 5, input `scheduler` for node "KSampler" id 29 (autogenerated)',
)

parser.add_argument(
    "--denoise35",
    default=1,
    help='Argument 9, input `denoise` for node "KSampler" id 29 (autogenerated)',
)

parser.add_argument(
    "--filename_prefix36",
    default="ComfyUI",
    help='Argument 1, input `filename_prefix` for node "Save Video" id 3 (autogenerated)',
)

parser.add_argument(
    "--format37",
    default="auto",
    help='Argument 2, input `format` for node "Save Video" id 3 (autogenerated)',
)

parser.add_argument(
    "--codec38",
    default="auto",
    help='Argument 3, input `codec` for node "Save Video" id 3 (autogenerated)',
)

parser.add_argument(
    "--queue-size",
    "-q",
    type=int,
    default=1,
    help="How many times the workflow will be executed (default: 1)",
)

parser.add_argument(
    "--comfyui-directory",
    "-c",
    default=None,
    help="Where to look for ComfyUI (default: current directory)",
)

parser.add_argument(
    "--output",
    "-o",
    default=None,
    help="The location to save the output image. Either a file path, a directory, or - for stdout (default: the ComfyUI output directory)",
)

parser.add_argument(
    "--disable-metadata",
    action="store_true",
    help="Disables writing workflow metadata to the outputs",
)


comfy_args = [sys.argv[0]]
if __name__ == "__main__" and "--" in sys.argv:
    idx = sys.argv.index("--")
    comfy_args += sys.argv[idx + 1 :]
    sys.argv = sys.argv[:idx]

args = None
if __name__ == "__main__":
    args = parser.parse_args()
    sys.argv = comfy_args
if args is not None and args.output is not None and args.output == "-":
    ctx = contextlib.redirect_stdout(sys.stderr)
else:
    ctx = contextlib.nullcontext()

PROMPT_DATA = json.loads(
    '{"1": {"inputs": {"trim_amount": ["25", 3], "samples": ["29", 0]}, "class_type": "TrimVideoLatent", "_meta": {"title": "TrimVideoLatent"}}, "2": {"inputs": {"shift": 8, "model": ["11", 0]}, "class_type": "ModelSamplingSD3", "_meta": {"title": "ModelSamplingSD3"}}, "3": {"inputs": {"filename_prefix": "video/ComfyUI", "format": "auto", "codec": "auto", "video": ["4", 0]}, "class_type": "SaveVideo", "_meta": {"title": "Save Video"}}, "4": {"inputs": {"fps": ["22", 5], "images": ["33", 0]}, "class_type": "CreateVideo", "_meta": {"title": "Create Video"}}, "10": {"inputs": {"unet_name": "wan2.1_vace_14B_fp16.safetensors", "weight_dtype": "fp8_e4m3fn_fast"}, "class_type": "UNETLoader", "_meta": {"title": "Load Diffusion Model"}}, "11": {"inputs": {"lora_name": "Wan21_CausVid_14B_T2V_lora_rank32.safetensors", "strength_model": 0.30000000000000004, "model": ["10", 0]}, "class_type": "LoraLoaderModelOnly", "_meta": {"title": "LoraLoaderModelOnly"}}, "12": {"inputs": {"clip_name": "umt5_xxl_fp8_e4m3fn_scaled.safetensors", "type": "wan", "device": "default"}, "class_type": "CLIPLoader", "_meta": {"title": "Load CLIP"}}, "13": {"inputs": {"vae_name": "wan_2.1_vae.safetensors"}, "class_type": "VAELoader", "_meta": {"title": "Load VAE"}}, "18": {"inputs": {"mask": ["28", 2]}, "class_type": "MaskToImage", "_meta": {"title": "Convert Mask to Image"}}, "20": {"inputs": {"samples": ["1", 0], "vae": ["13", 0]}, "class_type": "VAEDecode", "_meta": {"title": "VAE Decode"}}, "21": {"inputs": {"mask": ["28", 2]}, "class_type": "InvertMask", "_meta": {"title": "InvertMask"}}, "22": {"inputs": {"video_info": ["26", 3]}, "class_type": "VHS_VideoInfo", "_meta": {"title": "Video Info \\ud83c\\udfa5\\ud83c\\udd65\\ud83c\\udd57\\ud83c\\udd62"}}, "24": {"inputs": {"text": "three pepsi cans spinning from above", "clip": ["12", 0]}, "class_type": "CLIPTextEncode", "_meta": {"title": "CLIP Text Encode (Positive Prompt)"}}, "25": {"inputs": {"width": 720, "height": 720, "length": 41, "batch_size": 1, "strength": 1, "positive": ["24", 0], "negative": ["30", 0], "vae": ["13", 0], "control_video": ["31", 0], "reference_image": ["32", 0]}, "class_type": "WanVaceToVideo", "_meta": {"title": "WanVaceToVideo"}}, "26": {"inputs": {"video": "4465010-hd_1920_1080_30fps.mp4", "force_rate": 0, "custom_width": 720, "custom_height": 720, "frame_load_cap": 41, "skip_first_frames": 0, "select_every_nth": 1, "format": "Wan"}, "class_type": "VHS_LoadVideo", "_meta": {"title": "Load Video (Upload) \\ud83c\\udfa5\\ud83c\\udd65\\ud83c\\udd57\\ud83c\\udd62"}}, "27": {"inputs": {"mask": ["28", 2]}, "class_type": "MaskPreview", "_meta": {"title": "Preview Mask"}}, "28": {"inputs": {"prompt": "coke bottle", "threshold": 0.4, "min_width_pixels": 0, "min_height_pixels": 0, "use_video_model": true, "unload_after_run": true, "object_ids": "", "image": ["26", 0]}, "class_type": "SAM3Segmentation", "_meta": {"title": "SAM3 Segmentation"}}, "29": {"inputs": {"seed": 812152535208420, "steps": 4, "cfg": 1, "sampler_name": "uni_pc", "scheduler": "simple", "denoise": 1, "model": ["2", 0], "positive": ["25", 0], "negative": ["25", 1], "latent_image": ["25", 2]}, "class_type": "KSampler", "_meta": {"title": "KSampler"}}, "30": {"inputs": {"text": "black background, mask, blurry, unrealistic, poor quality, animated, poorly drawn", "clip": ["12", 0]}, "class_type": "CLIPTextEncode", "_meta": {"title": "CLIP Text Encode (Negative Prompt)"}}, "31": {"inputs": {"image_from": ["18", 0], "image_to": ["26", 0], "mask": ["21", 0]}, "class_type": "ImageCompositeFromMaskBatch+", "_meta": {"title": "\\ud83d\\udd27 Image Composite From Mask Batch"}}, "32": {"inputs": {"image": "300Wx300H-1-HYK-24769.jpg"}, "class_type": "LoadImage", "_meta": {"title": "Load Image"}}, "33": {"inputs": {"image_from": ["20", 0], "image_to": ["26", 0], "mask": ["21", 0]}, "class_type": "ImageCompositeFromMaskBatch+", "_meta": {"title": "\\ud83d\\udd27 Image Composite From Mask Batch"}}, "34": {"inputs": {"images": ["20", 0]}, "class_type": "PreviewImage", "_meta": {"title": "Preview Image"}}, "35": {"inputs": {"images": ["26", 0]}, "class_type": "PreviewImage", "_meta": {"title": "Preview Image"}}, "36": {"inputs": {"images": ["31", 0]}, "class_type": "PreviewImage", "_meta": {"title": "Preview Image"}}, "42": {"inputs": {"images": ["33", 0]}, "class_type": "PreviewImage", "_meta": {"title": "Preview Image"}}}'
)


def import_custom_nodes() -> None:
    """Find all custom nodes in the custom_nodes folder and add those node objects to NODE_CLASS_MAPPINGS

    This function sets up a new asyncio event loop, initializes the PromptServer,
    creates a PromptQueue, and initializes the custom nodes.
    """
    if has_manager:
        try:
            import manager_core as manager
        except ImportError:
            print("Could not import manager_core, proceeding without it.")
            return
        else:
            if hasattr(manager, "get_config"):
                print("Patching manager_core.get_config to enforce offline mode.")
                try:
                    get_config = manager.get_config

                    def _get_config(*args, **kwargs):
                        config = get_config(*args, **kwargs)
                        config["network_mode"] = "offline"
                        return config

                    manager.get_config = _get_config
                except Exception as e:
                    print("Failed to patch manager_core.get_config:", e)

    import asyncio
    import execution
    from nodes import init_extra_nodes
    import server

    # Creating a new event loop and setting it as the default loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def inner():
        # Creating an instance of PromptServer with the loop
        server_instance = server.PromptServer(loop)
        execution.PromptQueue(server_instance)

        # Initializing custom nodes
        await init_extra_nodes(init_custom_nodes=True)

    loop.run_until_complete(inner())


_custom_nodes_imported = False
_custom_path_added = False
_output_directory_set = False


def ensure_output_directory():
    global _output_directory_set
    if _output_directory_set:
        return
    script_dir = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
    try:
        from folder_paths import set_output_directory
    except ImportError:
        return
    set_output_directory(script_dir)
    _output_directory_set = True


def main(*func_args, **func_kwargs):
    global args, _custom_nodes_imported, _custom_path_added
    if __name__ == "__main__":
        if args is None:
            args = parser.parse_args()
    else:
        defaults = dict(
            (arg, parser.get_default(arg))
            for arg in ["queue_size", "comfyui_directory", "output", "disable_metadata"]
            + [
                "unet_name1",
                "weight_dtype2",
                "lora_name3",
                "strength_model4",
                "clip_name5",
                "type6",
                "vae_name7",
                "text8",
                "video9",
                "force_rate10",
                "custom_width11",
                "custom_height12",
                "frame_load_cap13",
                "skip_first_frames14",
                "select_every_nth15",
                "text16",
                "image17",
                "prompt18",
                "threshold19",
                "min_width_pixels20",
                "min_height_pixels21",
                "use_video_model22",
                "unload_after_run23",
                "width24",
                "height25",
                "length26",
                "batch_size27",
                "strength28",
                "shift29",
                "seed30",
                "steps31",
                "cfg32",
                "sampler_name33",
                "scheduler34",
                "denoise35",
                "filename_prefix36",
                "format37",
                "codec38",
            ]
        )

        all_args = dict()
        all_args.update(defaults)
        all_args.update(func_kwargs)

        args = argparse.Namespace(**all_args)

    with ctx:
        if not _custom_path_added:
            add_comfyui_directory_to_sys_path()
            add_extra_model_paths()

            _custom_path_added = True

        if not _custom_nodes_imported:
            import_custom_nodes()

            _custom_nodes_imported = True

        from nodes import NODE_CLASS_MAPPINGS
        ensure_output_directory()

        def instantiate_node(node_name: str):
            node_cls = NODE_CLASS_MAPPINGS[node_name]
            prepare_clone = getattr(node_cls, "PREPARE_CLASS_CLONE", None)
            if callable(prepare_clone):
                node_cls = node_cls.PREPARE_CLASS_CLONE(None)
            return node_cls()

    with torch.inference_mode(), ctx:
        unetloader = instantiate_node("UNETLoader")
        unetloader_10 = unetloader.load_unet(
            unet_name=parse_arg(args.unet_name1),
            weight_dtype=parse_arg(args.weight_dtype2),
        )

        loraloadermodelonly = instantiate_node("LoraLoaderModelOnly")
        loraloadermodelonly_11 = loraloadermodelonly.load_lora_model_only(
            lora_name=parse_arg(args.lora_name3),
            strength_model=parse_arg(args.strength_model4),
            model=get_value_at_index(unetloader_10, 0),
        )

        cliploader = instantiate_node("CLIPLoader")
        cliploader_12 = cliploader.load_clip(
            clip_name=parse_arg(args.clip_name5),
            type=parse_arg(args.type6),
            device="default",
        )

        vaeloader = instantiate_node("VAELoader")
        vaeloader_13 = vaeloader.load_vae(vae_name=parse_arg(args.vae_name7))

        cliptextencode = instantiate_node("CLIPTextEncode")
        cliptextencode_24 = cliptextencode.encode(
            text=parse_arg(args.text8), clip=get_value_at_index(cliploader_12, 0)
        )

        vhs_loadvideo = instantiate_node("VHS_LoadVideo")
        vhs_loadvideo_26 = vhs_loadvideo.load_video(
            video=parse_arg(args.video9),
            force_rate=parse_arg(args.force_rate10),
            custom_width=parse_arg(args.custom_width11),
            custom_height=parse_arg(args.custom_height12),
            frame_load_cap=parse_arg(args.frame_load_cap13),
            skip_first_frames=parse_arg(args.skip_first_frames14),
            select_every_nth=parse_arg(args.select_every_nth15),
            format="Wan",
        )

        cliptextencode_30 = cliptextencode.encode(
            text=parse_arg(args.text16), clip=get_value_at_index(cliploader_12, 0)
        )

        loadimage = instantiate_node("LoadImage")
        loadimage_32 = loadimage.load_image(image=parse_arg(args.image17))

        sam3segmentation = instantiate_node("SAM3Segmentation")
        masktoimage = instantiate_node("MaskToImage")
        invertmask = instantiate_node("InvertMask")
        imagecompositefrommaskbatch = instantiate_node("ImageCompositeFromMaskBatch+")
        wanvacetovideo = instantiate_node("WanVaceToVideo")
        modelsamplingsd3 = instantiate_node("ModelSamplingSD3")
        ksampler = instantiate_node("KSampler")
        trimvideolatent = instantiate_node("TrimVideoLatent")
        vhs_videoinfo = instantiate_node("VHS_VideoInfo")
        vaedecode = instantiate_node("VAEDecode")
        createvideo = instantiate_node("CreateVideo")
        savevideo = instantiate_node("SaveVideo")
        maskpreview = instantiate_node("MaskPreview")
        for q in range(args.queue_size):
            sam3segmentation_28 = sam3segmentation.segment(
                prompt=parse_arg(args.prompt18),
                threshold=parse_arg(args.threshold19),
                min_width_pixels=parse_arg(args.min_width_pixels20),
                min_height_pixels=parse_arg(args.min_height_pixels21),
                use_video_model=parse_arg(args.use_video_model22),
                unload_after_run=parse_arg(args.unload_after_run23),
                object_ids="",
                image=get_value_at_index(vhs_loadvideo_26, 0),
            )

            masktoimage_18 = masktoimage.EXECUTE_NORMALIZED(
                mask=get_value_at_index(sam3segmentation_28, 2)
            )

            invertmask_21 = invertmask.EXECUTE_NORMALIZED(
                mask=get_value_at_index(sam3segmentation_28, 2)
            )

            imagecompositefrommaskbatch_31 = imagecompositefrommaskbatch.execute(
                image_from=get_value_at_index(masktoimage_18, 0),
                image_to=get_value_at_index(vhs_loadvideo_26, 0),
                mask=get_value_at_index(invertmask_21, 0),
            )

            wanvacetovideo_25 = wanvacetovideo.EXECUTE_NORMALIZED(
                width=parse_arg(args.width24),
                height=parse_arg(args.height25),
                length=parse_arg(args.length26),
                batch_size=parse_arg(args.batch_size27),
                strength=parse_arg(args.strength28),
                positive=get_value_at_index(cliptextencode_24, 0),
                negative=get_value_at_index(cliptextencode_30, 0),
                vae=get_value_at_index(vaeloader_13, 0),
                control_video=get_value_at_index(imagecompositefrommaskbatch_31, 0),
                reference_image=get_value_at_index(loadimage_32, 0),
            )

            modelsamplingsd3_2 = modelsamplingsd3.patch(
                shift=parse_arg(args.shift29),
                model=get_value_at_index(loraloadermodelonly_11, 0),
            )

            ksampler_29 = ksampler.sample(
                seed=parse_arg(args.seed30),
                steps=parse_arg(args.steps31),
                cfg=parse_arg(args.cfg32),
                sampler_name=parse_arg(args.sampler_name33),
                scheduler=parse_arg(args.scheduler34),
                denoise=parse_arg(args.denoise35),
                model=get_value_at_index(modelsamplingsd3_2, 0),
                positive=get_value_at_index(wanvacetovideo_25, 0),
                negative=get_value_at_index(wanvacetovideo_25, 1),
                latent_image=get_value_at_index(wanvacetovideo_25, 2),
            )

            trimvideolatent_1 = trimvideolatent.EXECUTE_NORMALIZED(
                trim_amount=get_value_at_index(wanvacetovideo_25, 3),
                samples=get_value_at_index(ksampler_29, 0),
            )

            vhs_videoinfo_22 = vhs_videoinfo.get_video_info(
                video_info=get_value_at_index(vhs_loadvideo_26, 3)
            )

            vaedecode_20 = vaedecode.decode(
                samples=get_value_at_index(trimvideolatent_1, 0),
                vae=get_value_at_index(vaeloader_13, 0),
            )

            imagecompositefrommaskbatch_33 = imagecompositefrommaskbatch.execute(
                image_from=get_value_at_index(vaedecode_20, 0),
                image_to=get_value_at_index(vhs_loadvideo_26, 0),
                mask=get_value_at_index(invertmask_21, 0),
            )

            createvideo_4 = createvideo.EXECUTE_NORMALIZED(
                fps=get_value_at_index(vhs_videoinfo_22, 5),
                images=get_value_at_index(imagecompositefrommaskbatch_33, 0),
            )

            savevideo_3 = savevideo.EXECUTE_NORMALIZED(
                filename_prefix=parse_arg(args.filename_prefix36),
                format=parse_arg(args.format37),
                codec=parse_arg(args.codec38),
                video=get_value_at_index(createvideo_4, 0),
            )

            maskpreview_27 = maskpreview.EXECUTE_NORMALIZED(
                mask=get_value_at_index(sam3segmentation_28, 2)
            )


if __name__ == "__main__":
    main()
