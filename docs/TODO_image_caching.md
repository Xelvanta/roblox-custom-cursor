TODO: Image caching for preserving quality when downscaling and then upscaling

"How can we resample then cache an image to memory if its not cached already and if it is, call the cached image instead of resampling it again? Also consider if the cache has to match the position of the image. For example, if the image is nudged 1px left and the rest of the canvas is filled with transparent pixels, then how can downsampling, nudging left, then upsampling avoid resampling?"

Suggestion: **Always keep the original image in cache without position modifications, then everytime a resample is requested, lazily cache the resample from the original then apply the position in the app, but dont cache that version**

---

## 🔄 Workflow Description

1. **Upload or Import a New Image**

   * User selects a file → app loads it.
   * `clear_resample_cache()` is called to ensure no stale data remains.
   * The **original image** is stored in `self.resample_cache["original"]` without any position modifications.

2. **Resampling on Demand**

   * When a resized image is requested (`get_resized_image(target_size)`):

     * Check if a cached version for that size exists → return it.
     * If not, **resample directly from the original image** using **Lanczos**.
     * Store the newly resampled image in `self.resample_cache[target_size]`.
     * Apply any position offsets **in the app**, but **do not cache the positioned version**.

3. **Subsequent Operations**

   * All future resize calls reuse cached resampled versions if available.
   * Position modifications are applied dynamically at runtime and never alter the cached original or resampled images.
   * Cache persists until a new image is uploaded or imported, at which point `clear_resample_cache()` resets everything.
