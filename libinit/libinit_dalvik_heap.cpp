/*
 * Copyright (C) 2021 The LineageOS Project
 *
 * SPDX-License-Identifier: Apache-2.0
 */

#include <sys/sysinfo.h>
#include <libinit_utils.h>

#include <libinit_dalvik_heap.h>

#define HEAPSTARTSIZE_PROP "dalvik.vm.heapstartsize"
#define HEAPGROWTHLIMIT_PROP "dalvik.vm.heapgrowthlimit"
#define HEAPSIZE_PROP "dalvik.vm.heapsize"
#define HEAPMINFREE_PROP "dalvik.vm.heapminfree"
#define HEAPMAXFREE_PROP "dalvik.vm.heapmaxfree"
#define HEAPTARGETUTILIZATION_PROP "dalvik.vm.heaptargetutilization"

#define GB(b) (b * 1024ull * 1024 * 1024)

static const dalvik_heap_info_t dalvik_heap_info_6144 = {
    .heapstartsize = "16m",
    .heapgrowthlimit = "256m",
    .heapsize = "512m",
    .heapminfree = "8m",
    .heapmaxfree = "32m",
    .heaptargetutilization = "0.5",
};

static const dalvik_heap_info_t dalvik_heap_info_4096 = {
    .heapstartsize = "8m",
    .heapgrowthlimit = "256m",
    .heapsize = "512m",
    .heapminfree = "8m",
    .heapmaxfree = "16m",
    .heaptargetutilization = "0.6",
};

static const dalvik_heap_info_t dalvik_heap_info_2048 = {
    .heapstartsize = "8m",
    .heapgrowthlimit = "192m",
    .heapsize = "512m",
    .heapminfree = "512k",
    .heapmaxfree = "8m",
    .heaptargetutilization = "0.75",
};

void set_dalvik_heap() {
    struct sysinfo sys;
    const dalvik_heap_info_t *dhi;

    sysinfo(&sys);

    if (sys.totalram > GB(5))
        dhi = &dalvik_heap_info_6144;
    else if (sys.totalram > GB(3))
        dhi = &dalvik_heap_info_4096;
    else
        dhi = &dalvik_heap_info_2048;

    /* Set props for 4GB Users */
    property_override("ro.config.fha_enable", "true");
	property_override("ro.sys.fw.bg_apps_limit", "32");
	property_override("ro.config.dha_cached_max", "16");
	property_override("ro.config.dha_empty_max", "42");
	property_override("ro.config.dha_empty_init", "32");
	property_override("ro.config.dha_lmk_scale", "0.545");
	property_override("ro.config.dha_th_rate", "2.3");
	property_override("ro.config.sdha_apps_bg_max", "64");
	property_override("ro.config.sdha_apps_bg_min", "8");

    property_override(HEAPSTARTSIZE_PROP, dhi->heapstartsize);
    property_override(HEAPGROWTHLIMIT_PROP, dhi->heapgrowthlimit);
    property_override(HEAPSIZE_PROP, dhi->heapsize);
    property_override(HEAPTARGETUTILIZATION_PROP, dhi->heaptargetutilization);
    property_override(HEAPMINFREE_PROP, dhi->heapminfree);
    property_override(HEAPMAXFREE_PROP, dhi->heapmaxfree);
}
