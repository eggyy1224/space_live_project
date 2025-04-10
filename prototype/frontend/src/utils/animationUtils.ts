/**
 * Extracts a user-friendly animation name from a file path.
 * Example: /animations/RunningArc_animation.glb -> RunningArc
 * @param path The full path to the animation file.
 * @returns A friendly name for the animation.
 */
export function getFriendlyAnimationName(path: string): string {
  // 1. Get the filename from the path (e.g., "RunningArc_animation.glb")
  const filename = path.split('/').pop() || '';
  
  // 2. Remove common suffixes like "_animation.glb" or ".glb"
  const nameWithoutSuffix = filename
    .replace(/_animation\.glb$/i, '') // Remove "_animation.glb" (case-insensitive)
    .replace(/\.glb$/i, '');          // Remove ".glb" if the first didn't match

  // 3. Optional: Replace underscores with spaces for better readability
  // const friendlyName = nameWithoutSuffix.replace(/_/g, ' ');
  // For now, let's keep underscores or use CamelCase if present
  const friendlyName = nameWithoutSuffix;

  return friendlyName || path; // Return the processed name or the original path as fallback
} 