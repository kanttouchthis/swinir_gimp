#!/usr/bin/env python

from gimpfu import *
import os
import subprocess

PYTHON = "/path/to/python.exe" # change this to your python path
SWINIR = "/path/to/SwinIR" # change this to the path of SwinIR
SCRIPT = "main_test_swinir.py"
TILE = "400" # Tile size. Reduce if you run out of memory.

# Models
class realSR2M:
    task = "real_sr"
    model_path = SWINIR + "/model_zoo/swinir/003_realSR_BSRGAN_DFO_s64w8_SwinIR-M_x2_GAN.pth"
    folder_lq = SWINIR + "/input/"
    out_path = SWINIR + "/results/swinir_real_sr_x2/"
    large_model = False
    scale = 2

class realSR4M:
    task = "real_sr"
    model_path = SWINIR + "/model_zoo/swinir/003_realSR_BSRGAN_DFO_s64w8_SwinIR-M_x4_GAN.pth"
    folder_lq = SWINIR + "/input/"
    out_path = SWINIR + "/results/swinir_real_sr_x4/"
    large_model = False
    scale = 4

class realSR4L:
    task = "real_sr"
    model_path = SWINIR + "/model_zoo/swinir/003_realSR_BSRGAN_DFOWMFC_s64w8_SwinIR-L_x4_GAN.pth"
    folder_lq = SWINIR + "/input/"
    out_path = SWINIR +"/results/swinir_real_sr_x4_large/"
    large_model = True
    scale = 4

class colorDN15:
    task = "color_dn"
    model_path = SWINIR + "/model_zoo/swinir/005_colorDN_DFWB_s128w8_SwinIR-M_noise15.pth"
    folder_gt = SWINIR + "/input/"
    out_path = SWINIR + "/results/swinir_color_dn_noise0/"
    noise = 0

class colorDN25:
    task = "color_dn"
    model_path = SWINIR + "/model_zoo/swinir/005_colorDN_DFWB_s128w8_SwinIR-M_noise25.pth"
    folder_gt = SWINIR + "/input/"
    out_path = SWINIR + "/results/swinir_color_dn_noise0/"
    noise = 0

class colorDN50:
    task = "color_dn"
    model_path = SWINIR + "/model_zoo/swinir/005_colorDN_DFWB_s128w8_SwinIR-M_noise50.pth"
    folder_gt = SWINIR + "/input/"
    out_path = SWINIR + "/results/swinir_color_dn_noise0/"
    noise = 0

class Models:
    realSR2M = realSR2M
    realSR4M = realSR4M
    realSR4L = realSR4L
    colorDN15 = colorDN15
    colorDN25 = colorDN25
    colorDN50 = colorDN50

def get_cmd(Model):
    if Model.task == "real_sr":
        cmd = [PYTHON, SCRIPT, "--task", Model.task,"--model_path", Model.model_path, "--folder_lq", Model.folder_lq, "--scale", str(Model.scale), "--tile", TILE]
        if Model.large_model:
            cmd.append("--large_model")
    elif Model.task == "color_dn":
        cmd = [PYTHON, SCRIPT, "--task", Model.task,"--model_path", Model.model_path, "--folder_gt", Model.folder_gt, "--noise", str(Model.noise), "--tile", TILE]
    else:
        raise Exception("Unknown task: " + Model.task)
    return cmd

def run_model(image, drawable, Model):
    os.chdir(SWINIR)
    # Save temp image
    if hasattr(Model, "folder_lq"):
        input_folder = Model.folder_lq
    else:
        input_folder = Model.folder_gt
    try:
        os.mkdir(input_folder)
    except OSError as e:
        print(e)
        pass

    input_filename = input_folder + "swinir_gimp_temp.png"
    pdb.gimp_edit_copy(image.active_drawable)
    image_temp = pdb.gimp_edit_paste_as_new()
    pdb.file_png_save(image_temp, drawable, input_filename, input_filename, 0, 9, 1, 1, 0, 1, 1)
    # Run model
    cmd = get_cmd(Model)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.wait()
    # Load output image
    output_filename = Model.out_path + "swinir_gimp_temp_SwinIR.png"
    image_temp = pdb.file_png_load(output_filename, output_filename)
    pdb.gimp_display_new(image_temp)
    gimp.displays_flush()

register(
        "SwinIR",
        "SwinIR",
        "",
        "kanttouchthis",
        "",
        "2022",
        "SwinIR",
        "*",
        [
            (PF_IMAGE, "image", "Input image", None),
            (PF_DRAWABLE, "drawable", "Input drawable", None),
            (PF_RADIO, "model", "choose model: ", Models.realSR4L,
            (
                ("realSR2M", Models.realSR2M),
                ("realSR4M", Models.realSR4M),
                ("realSR4L", Models.realSR4L),
                ("colorDN15", Models.colorDN15),
                ("colorDN25", Models.colorDN25),
                ("colorDN50", Models.colorDN50),
            )
         )
        ],
        [],
        run_model,
        menu = "<Image>/Filters/Enhance/"
)
main()
