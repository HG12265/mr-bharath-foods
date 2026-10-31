# Bharath Delight — Design update

Updated Home, About, Shop, Our Promise (including aliases), and Contact banners using the supplied Word document style: cream backgrounds, dark green serif headings, gold accents and existing family/product artwork. Mobile layouts stack readable text and artwork; desktop layouts retain the text/image composition.

All existing navigation destinations are retained. The header uses a mobile drawer on tablet widths to avoid overlapping links. Drawer accessibility includes Escape, focus handling and scroll locking. Shop toolbar controls now wrap on narrow screens.

Backend files and original public assets are byte-for-byte unchanged. No database, authentication, checkout or other business logic was changed.

## Validation
- Production build and TypeScript validation completed.
- Five main pages inspected at 320, 390, 768, 1024 and 1440 pixel frame widths. 23 of 25 initial checks had no horizontal overflow; Shop's two narrow-width checks identified the toolbar issue, corrected with flex wrapping.
- The final toolbar correction could not be visually rechecked because browser access reached its usage limit.
- Backend-dependent account/order flows were not tested as part of this design-only update.

## Run
Keep your existing backend/.env and frontend/.env.local files when applying this update. Actual environment files are excluded from this distribution; the existing environment examples remain included.

In frontend, run `npm ci`, then `npm run dev`. For production, run `npm run build`, then `npm start`.

Use the existing backend setup instructions and your existing database. This uploaded project uses Next.js and Python; its stack has been preserved.

Dependencies, build caches, Python caches and Git history are excluded from the ZIP. Existing source files and assets are included.
