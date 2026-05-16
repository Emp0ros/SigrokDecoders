# Xbox One I2C Protocol Decoders (Sigrok / Pulseview)

## Quick Start

### Deploy on Linux

1. **Locate the sigrok decoders directory:**
   ```bash
   sigrok-cli --version  # Find libsigrokdecode path
   # Usually: ~/.local/share/libsigrokdecode/decoders/ or /usr/share/libsigrokdecode/decoders/
   ```

2. **Create decoder directory:**
   ```bash
   mkdir -p ~/.local/share/libsigrokdecode/decoders/{max6958,xbox_one_sb_post,xbox_one_soc_post}
   ```

3. **Copy decoder files:**
   ```bash
   cp max6958/* ~/.local/share/libsigrokdecode/decoders/max6958/
   cp xbox_one_sb_post/* ~/.local/share/libsigrokdecode/decoders/xbox_one_sb_post/
   cp xbox_one_soc_post/* ~/.local/share/libsigrokdecode/decoders/xbox_one_soc_post/
   ```

4. **Verify installation:**
   ```bash
   sigrok-cli -L | grep -E 'xbox_one_sb_post|xbox_one_soc_post|max6958'
   ```

5. **Use in PulseView:**
   - Load I2C capture
   - Stack the I2C decoder
   - Stack respective sub-decoder from this repo
