#!/bin/sh

mkdir -p ~/.local/share/libsigrokdecode/decoders/max6958 && cp -r max6958/* ~/.local/share/libsigrokdecode/decoders/max6958/
mkdir -p ~/.local/share/libsigrokdecode/decoders/xbox_one_sb_post && cp -r xbox_one_sb_post/* ~/.local/share/libsigrokdecode/decoders/xbox_one_sb_post/
mkdir -p ~/.local/share/libsigrokdecode/decoders/xbox_one_soc_post && cp -r xbox_one_soc_post/* ~/.local/share/libsigrokdecode/decoders/xbox_one_soc_post/

# Test decoder
#clear; sigrok-cli -i i2c_trace.sr -P "i2c:sda=SB SDA:scl=SB SCL,max6958,xbox_one_sb_post"|grep -E 'max6958|xbox'
clear; sigrok-cli -i i2c_trace.sr -P "i2c:sda=SOC SDA:scl=SOC SCL,xbox_one_soc_post"|grep -E 'xbox_one_soc_post'
