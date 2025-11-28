#!/usr/bin/env -S PYTHONPATH=../../../tools/extract-utils python3
#
# SPDX-FileCopyrightText: 2024-2025 The LineageOS Project
# SPDX-License-Identifier: Apache-2.0
#

from extract_utils.fixups_blob import (
    BlobFixupCtx,
    File,
    blob_fixup,
    blob_fixups_user_type,
)
from extract_utils.fixups_lib import (
    lib_fixups,
    lib_fixups_user_type,
)
from extract_utils.main import (
    ExtractUtils,
    ExtractUtilsModule,
)
from extract_utils.tools import (
    llvm_objdump_path,
)
from extract_utils.utils import (
    run_cmd,
)

namespace_imports = [
    'device/xiaomi/miatoll',
    'hardware/qcom-caf/sm8150',
    'hardware/qcom-caf/wlan',
    'hardware/xiaomi',
    'vendor/qcom/opensource/commonsys-intf/display',
    'vendor/qcom/opensource/commonsys/display',
    'vendor/qcom/opensource/dataservices',
    'vendor/qcom/opensource/display',
]


def lib_fixup_vendor_suffix(lib: str, partition: str, *args, **kwargs):
    return f'{lib}_{partition}' if partition == 'vendor' else None

def blob_fixup_graphic_buffer_size(
    ctx: BlobFixupCtx,
    file: File,
    file_path: str,
    *args,
    **kwargs,
):
    for line in run_cmd(
        [
            llvm_objdump_path,
            '--disassemble-all',
            file_path,
        ]
    ).splitlines():
        line = line.split(maxsplit=5)
        if len(line) != 6:
            continue

        # The size of GraphicBuffer changed from 0x100 to 0xd30
        offset, _, instruction, register, value, _ = line
        if instruction == 'mov' and register[:-1] == 'w0' and value == '#0x100':
            with open(file_path, 'rb+') as f:
                f.seek(int(offset[:-1], 16))
                f.write(b'\x00\xa6\x81\x52')  # AArch64 mov w0, #0xd30

lib_fixups: lib_fixups_user_type = {
    **lib_fixups,
    (
        'com.qualcomm.qti.dpm.api@1.0',
        'libmmosal',
        'vendor.qti.hardware.fm@1.0',
        'vendor.qti.hardware.wifidisplaysession@1.0',
        'vendor.qti.imsrtpservice@3.0',
    ): lib_fixup_vendor_suffix,
}

blob_fixups: blob_fixups_user_type = {
    'system_ext/lib64/libwfdnative.so': blob_fixup()
        .add_needed('libinput_shim.so'),
    'vendor/etc/camera/camxoverridesettings.txt': blob_fixup()
        .regex_replace('0x10082', '0')
        .regex_replace('0x1F', '0x0'),
    'vendor/etc/init/android.hardware.keymaster@4.0-service-qti.rc': blob_fixup()
        .regex_replace('@4.0', '@4.1'),
    'vendor/lib64/camera/components/com.qti.node.watermark.so': blob_fixup()
        .add_needed('libpiex_shim.so'),
    'vendor/lib64/camera/components/com.vidhance.node.eis.so': blob_fixup()
        .call(blob_fixup_graphic_buffer_size),
    'vendor/lib64/hw/fingerprint.fpc.default.so': blob_fixup()
        .sig_replace('30 00 00 90 11 3A 42 F9', '30 00 00 90 1F 20 03 D5'),
    ('vendor/lib64/libalAILDC.so', 'vendor/lib64/libalLDC.so', 'vendor/lib64/libalhLDC.so'): blob_fixup()
        .clear_symbol_version('AHardwareBuffer_allocate')
        .clear_symbol_version('AHardwareBuffer_describe')
        .clear_symbol_version('AHardwareBuffer_lock')
        .clear_symbol_version('AHardwareBuffer_release')
        .clear_symbol_version('AHardwareBuffer_unlock'),
    ('vendor/lib64/libhvx_interface.so', 'vendor/lib64/libmialgo_rfs.so', 'vendor/lib64/libVDSuperPhotoAPI.so', 'vendor/lib64/libsnpe_dsp_domains_v2.so'): blob_fixup()
        .clear_symbol_version('remote_handle_close')
        .clear_symbol_version('remote_handle_invoke')
        .clear_symbol_version('remote_handle_open')
        .clear_symbol_version('remote_handle64_close')
        .clear_symbol_version('remote_handle64_invoke')
        .clear_symbol_version('remote_handle64_open')
        .clear_symbol_version('remote_register_dma_handle')
        .clear_symbol_version('remote_register_buf_attr')
        .clear_symbol_version('remote_register_buf'),
    'vendor/lib64/libgoodixhwfingerprint.so': blob_fixup()
        .replace_needed('libvendor.goodix.hardware.biometrics.fingerprint@2.1.so', 'vendor.goodix.hardware.biometrics.fingerprint@2.1.so'),
    'vendor/lib64/libwvhidl.so': blob_fixup()
        .add_needed('libcrypto_shim.so'),
}  # fmt: skip

module = ExtractUtilsModule(
    'miatoll',
    'xiaomi',
    blob_fixups=blob_fixups,
    lib_fixups=lib_fixups,
    namespace_imports=namespace_imports,
)

if __name__ == '__main__':
    utils = ExtractUtils.device(module)
    utils.run()
