# npm silently omits devDependencies — reproduction & fix

## Environment trigger
A `~/.npmrc` (or project `.npmrc`) containing:
```
omit[]=dev
```
combined with `NODE_ENV=production`. This is a PERSISTENT machine config for this user, not a transient error.

## Reproduce
```
npm create vite@latest myapp -- --template react-ts
cd myapp
npm install            # reports only a few packages, e.g. "added 3 packages"
npm run build          # FAILS:
                        # error TS2688: Cannot find type definition file for 'vite/client'.
                        # error TS2688: Cannot find type definition file for 'node'.
```

## Diagnose
```
npm config get omit          # -> "dev"  (this is the smoking gun)
npm config get production    # -> null
echo $NODE_ENV               # -> production
ls node_modules/@types       # -> empty
ls -d node_modules/vite      # -> missing (vite is a devDependency)
```

## Fix
```
npm install --include=dev    # re-pulls vite, typescript, @types/*, @vitejs/plugin-react
npm run build                # now succeeds: "✓ built in ~570ms"
```

## Why this bites
`create-vite` puts `vite`, `typescript`, `@types/node`, `@types/react`, `@vitejs/plugin-react` all in `devDependencies`. With `omit[]=dev`, `npm install` skips them. `tsc -b` fails on `types: ["vite/client"]` / `["node"]` in tsconfig because those type packages never landed. The error message points at TypeScript, not at the missing install — hence the misdiagnosis risk.
