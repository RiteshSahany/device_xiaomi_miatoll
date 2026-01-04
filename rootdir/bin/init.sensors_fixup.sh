#!/vendor/bin/sh
#
# SPDX-FileCopyrightText: The LineageOS Project
# SPDX-License-Identifier: Apache-2.0
#

sed -i '/sensor_temperature/d' /mnt/vendor/persist/sensors/sensors_list.txt
