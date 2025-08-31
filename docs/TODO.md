# 📝 TODO: Image Resample Caching System

## Goals

* Ensure efficient resampling by caching resized versions of the cursor image.
* Delete cache whenever a new image is uploaded (so stale images aren’t used).
* Apply the same behavior to the importer workflow.
* Consider optional disk persistence for cache (future setting).

---

## ✅ Changes to Existing Functions

* **`change_button_action`** (cursor uploader in GUI):

  * [ ] Clear `self.resample_cache` immediately after selecting a new file.
  * [ ] Store the base resized image (`64x64`) in the cache as level `64`.
  * [ ] Save the resized PNG to disk as usual.

* **Importer function(s)** (any function that brings in `.rcur` or other cursor assets):

  * [ ] Clear `self.resample_cache` when a new cursor is imported.
  * [ ] Store the imported/resized base image in the cache as level `64`.

---

## 🆕 Helper Functions to Add

* **`get_resized_image(size: int) -> Image`**

  * [ ] Check `self.resample_cache` for the requested size.
  * [ ] If cached, return immediately.
  * [ ] If not cached:

    * Find the closest available size in cache (up or down).
    * Resample from that cached version using **Lanczos**.
    * Store the new size in `self.resample_cache[size]`.
    * Return it.

* **`clear_resample_cache()`**

  * [ ] Empty the cache dictionary.
  * [ ] Called inside `change_button_action` and importer functions.

---

## 🔄 Workflow Description

1. **Upload or Import a New Image**

   * User selects a file → app loads it.
   * `clear_resample_cache()` is called to avoid stale data.
   * Image is resized to **64x64 (base size)** and stored in `self.resample_cache[64]`.
   * Base version is saved to disk for Roblox.

2. **Resizing (Upsample/Downsample)**

   * Call `get_resized_image(target_size)`.
   * If already cached → return instantly.
   * If not cached → resample from the nearest cached version using **Lanczos** and store it.

3. **Subsequent Operations**

   * All future resize calls reuse cache if available.
   * Cache stays valid until another **upload/import** replaces the source.

---

## ⚠️ Integrity & Manual File Changes

* The cache assumes that the **source 64×64 image on disk** is always the same one the user uploaded or imported.
* If the user **manually edits or replaces the cursor file in the filesystem**, the cache could become stale or invalid.

**Lazy Hash-Check Workflow (on resample request):**

1. Store a **hash (e.g., SHA256)** of the base 64×64 image at upload/import time (`self.base_hash`).
2. Whenever `get_resized_image()` is called:

   * Compute the hash of the on-disk 64×64 image.
   * Compare it to `self.base_hash`.
   * If the hash matches → cache is valid, return cached version.
   * If the hash differs → assume manual change:

     * Clear `self.resample_cache`.
     * Reload the base 64×64 from disk.
     * Update `self.base_hash`.
     * Rebuild the requested resample from the new file.

* This approach ensures the cache is **always consistent with the on-disk base image**, without needing constant monitoring.
* Hashing a 64×64 PNG is negligible in performance and only occurs lazily, **on demand**.
 
---

## ❗ Why Resample Caching is Necessary

1. **Prevent cumulative quality loss**

   * Without caching, each shrink/enlarge operation opens the **already-resized file from disk**.
   * Downsampling → upsampling repeatedly introduces **blurring and artifacts**.
   * By caching every resized version in memory, the app can always restore the exact pixels of any previously generated size.

2. **Improve performance**

   * Recomputing resized images repeatedly with Lanczos is **CPU-intensive**, even for small 64×64 images.
   * Cached versions allow instant retrieval without repeated resampling.

3. **Ensure consistency across GUI updates**

   * Every time the GUI preview or Roblox asset is updated, the same cached version can be used.
   * Guarantees that the displayed image matches exactly what will be saved to disk.

4. **Safe handling of multiple images**

   * When a user uploads a new image or imports a cursor, stale cache data from previous images could corrupt previews or operations.
   * Clearing the cache on upload/import ensures **all resizes come from the current source image**.

5. **Foundation for future features**

   * Memory/disk caching opens possibilities for:

     * Undo/redo functionality.
     * Persistent edits across sessions (if a disk cache is implemented).
     * More advanced non-destructive transformations.

---

## ⚙️ Future Consideration: Disk Cache

* [ ] Add an option to **cache images to disk** instead of/in addition to memory.

  * Could persist cache across app restarts.
  * Store in a `.cache` folder with hash-based filenames.
* [ ] Add a **setting** (e.g., "Enable Persistent Cache") to toggle this behavior.
* [ ] On new upload/import → delete the disk cache folder as well.
