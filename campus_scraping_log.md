# Campus Image Scraping Log
# Date: 2026-03-26
# Time: 18:10-19:45 GMT+8

## Network Issues Encountered

### Wikimedia (en.wikipedia.org, upload.wikimedia.org, commons.wikimedia.org)
COMPLETELY INACCESSIBLE from this exec environment. All TCP connections timeout.
- DNS resolution works fine (103.102.166.240 for upload.wikimedia.org)
- But TCP connections cannot be established (timeout after 30s)
- This was discovered after multiple retry attempts
- The one image that was successfully downloaded (CampusTsinghuaUniversity9.jpg at 18:27) 
  was from a separate test session before the network became restricted

### Successfully Accessed Sources
- Chinese university websites (tsinghua.edu.cn, pku.edu.cn, sjtu.edu.cn, zju.edu.cn, etc.) - ACCESSIBLE
- USTC website (ustc.edu.cn) - ACCESSIBLE
- HKUST website - ACCESSIBLE  
- Baidu.com - ACCESSIBLE
- Most international sites (Google, Wikimedia) - INACCESSIBLE

## Scraping Results Summary

### ✅ Complete (6/6 images)
- **HKU** (school_11399): 6 images, 3.4MB total
  - school_11399_1.png (92KB), _2.png (160KB), _3.jpg (1.4MB), _4.jpg (1.3MB), _5.jpg (483KB), _6.png (72KB)
  - Source: Pre-existing in database, all large high-quality photos
  
- **CUHK** (school_2156): 6 images, 1.0MB total
  - school_2156_1-6.jpg (138-205KB each)
  - Source: Pre-existing in database, all large high-quality photos

### ⚠️ Partial (some images)
- **Tsinghua** (school_13859): 4/6 images, 2.2MB total
  - Slot 1: 1.jpg (1.1MB) - from Wikimedia
  - Slot 2: 2.jpg (498KB) - from tsinghua.edu.cn
  - Slot 3: 3.jpg (127KB) - from tsinghua.edu.cn
  - Slot 4: 4.jpg (532KB) - from tsinghua.edu.cn
  - Missing: slots 5-6

- **Peking** (school_13858): 5/6 images, 0.2MB total
  - Slot 1: MISSING
  - Slot 2: 2.jpg (81KB) - from pku.edu.cn
  - Slot 3: 3.jpg (81KB) - from pku.edu.cn
  - Slot 4: 4.jpg (50KB) - from pku.edu.cn
  - Slot 5: 5.webp (16KB) - pre-existing
  - Slot 6: 6.webp (9KB) - pre-existing (TINY)

- **Fudan** (school_20692): 4/6 images, 0.9MB total
  - Slot 1-2: MISSING
  - Slot 3: 3.jpg (926KB) - from fudan.edu.cn
  - Slots 4-6: tiny 6-8KB webp files (pre-existing, too small)

- **USTC** (school_7136): 4/6 images, 2.2MB total
  - Slot 1-2: MISSING
  - Slot 3: 3.jpg (1928KB) - from ustc.edu.cn
  - Slot 4: 4.jpg (133KB) - from ustc.edu.cn
  - Slot 5: 5.jpg (133KB) - from ustc.edu.cn
  - Slot 6: 6.webp (9KB) - pre-existing (TINY)

- **HKUST** (school_20723): 5/6 images, 0.4MB total
  - Slot 1: MISSING
  - Slot 2: 2.jpg (166KB) - from hkust.edu.hk
  - Slot 3: 3.jpg (166KB) - from hkust.edu.hk
  - Slots 4-6: tiny 7-11KB webp files (pre-existing)

- **NUS** (school_17881): 5/6 images, tiny total
  - Slot 1: MISSING
  - Slots 2-6: tiny 6-14KB webp files (pre-existing, too small)

- **NTU Singapore** (school_13200): 4/6 images, 0.1MB total
  - Slot 1-2: MISSING
  - Slot 3: 3.jpg (108KB) - from ntu.edu.sg
  - Slots 4-6: tiny 9-21KB webp files (pre-existing)

### ❌ Missing all
- **Shanghai Jiao Tong University** (school_20694): 2/6 images, 2.2MB total
  - Slot 1: 1.jpg (1324KB) - from sjtu.edu.cn
  - Slot 2: 2.jpg (899KB) - from sjtu.edu.cn
  - Missing: slots 3-6

- **Zhejiang University** (school_20693): 3/6 images, 0.1MB total
  - Slot 1: 1.png (51KB) - pre-existing
  - Slot 2: 2.jpg (38KB) - from zju.edu.cn
  - Slot 3: 3.jpg (41KB) - from zju.edu.cn
  - Missing: slots 4-6

- **National Taiwan University** (school_11396): 1/6 images, 0.4MB
  - Slot 1: 1.jpg (450KB) - pre-existing
  - Missing: slots 2-6

## Root Cause Analysis
The host (Mac mini) appears to have network restrictions that block:
1. Wikimedia sites (en.wikipedia.org, upload.wikimedia.org)
2. Most international sites
3. NUS (nus.edu.sg) - returns only 212-char minimal content (blocking script)
4. NTU Taiwan (ntu.edu.tw) - SSL certificate verification issues

## Recommendations for Next Steps
1. **When network is available**: Run `python3 scrape_campus_images.py` to fill remaining slots
2. **Manual cleanup**: Consider replacing tiny 6-14KB webp files with actual photos
3. **Source alternatives**: Try Chinese mirror sites or VPNs for Wikimedia access

## Script Location
`scrape_campus_images.py` - ready to run when Wikimedia access is restored
