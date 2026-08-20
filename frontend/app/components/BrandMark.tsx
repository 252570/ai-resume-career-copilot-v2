/* Quiet Signal Studio: a self-contained compass-document mark that renders without network-dependent image loading. */
export function BrandMark() {
  return (
    <span className="mark" aria-hidden="true">
      <span className="mark-fallback" />
    </span>
  );
}
