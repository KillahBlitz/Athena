const nativeAnimate = Element.prototype.animate

Element.prototype.animate = function (...args: Parameters<Element['animate']>) {
  const animation = nativeAnimate.apply(this, args)
  animation.finished.catch(() => {})
  return animation
}
