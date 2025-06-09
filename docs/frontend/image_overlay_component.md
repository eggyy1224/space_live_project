# ImageOverlay Component

The `ImageOverlay` component listens for `generated-image` WebSocket messages and displays AI generated images on top of the scene. Images keep their original aspect ratio and disappear after the duration provided by the backend.

## Handling Aspect Ratios

- The backend sends an optional `aspect_ratio` value along with `url` and `duration`.
- The component uses `width` from `display_config` and lets the image height adjust automatically.
- CSS `object-fit: contain` ensures the full image is visible regardless of its proportions.

```ts
service.registerHandler('generated-image', (data) => {
  setImages(prev => [...prev, { url: data.url, aspect_ratio: data.aspect_ratio }]);
});
```

No fixed height is applied, so the browser calculates it from the image's intrinsic dimensions.

