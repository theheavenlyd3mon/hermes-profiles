# Vitest Unit Testing Patterns for MagicMirror² Modules

## Test File Conventions

- Location: `tests/unit/modules/<module-name>/<name>_spec.js`
- Suffix: `_spec.js` (not `.test.js` — project convention)
- Globals: `describe`, `it`, `expect`, `vi` are available without import (vitest globals)
- Vitest config: `vitest.config.js` at project root

## Testing Module Logic (No DOM)

For pure functions extracted to standalone files (e.g., `board-utils.js`):

```js
const { diffBoardState, statusToEvent, clamp } = require("../../../../modules/hermes-bridge/board-utils");

describe("board-utils", () => {
  describe("diffBoardState", () => {
    it("should emit TASK_CREATED for new tasks", () => {
      const prev = { tasks: [] };
      const curr = { tasks: [{ task_id: "1", title: "New", status: "ready" }] };
      const events = diffBoardState(prev, curr);
      expect(events).toHaveLength(1);
      expect(events[0].type).toBe("HERMES_KANBAN_TASK_CREATED");
    });
  });
});
```

## Testing Module UI (With DOM)

For modules that use `document.createElement()` — add jsdom directive at top:

```js
// @vitest-environment jsdom
```

### Mock Pattern for Module.register()

```js
describe("hermes-dashboard", () => {
  let dashboard;

  beforeEach(() => {
    global.Module = {
      register: vi.fn((name, moduleDefinition) => {
        dashboard = moduleDefinition;
      })
    };
    global.Log = {
      info: vi.fn(),
      warn: vi.fn(),
      error: vi.fn()
    };

    // Load the module (triggers Module.register)
    require("../../../../modules/hermes-dashboard/hermes-dashboard");

    // Setup instance
    dashboard.config = { ...dashboard.defaults };
    dashboard.name = "hermes-dashboard";
    dashboard.file = vi.fn((path) => `modules/hermes-dashboard/${path}`);
    dashboard.updateDom = vi.fn();
    dashboard.start();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("should handle notifications", () => {
    dashboard.notificationReceived("HERMES_KANBAN_TASK_CREATED", {
      task_id: "1", title: "Test", status: "ready"
    });
    expect(dashboard.tasks).toHaveLength(1);
    expect(dashboard.updateDom).toHaveBeenCalled();
  });
});
```

### Key Gotchas

1. **`Module.register` mock must capture the definition** — the mock callback assigns the second arg to a local variable. The variable IS the module (not an instance).

2. **`dashboard.config = { ...dashboard.defaults }`** — must copy defaults before testing. The module definition's `defaults` is the template; `config` is what methods read.

3. **`dashboard.file = vi.fn(...)`** — modules call `this.file()` to resolve CSS paths. Mock it or `getStyles()` will throw.

4. **`dashboard.updateDom = vi.fn()`** — prevents actual DOM updates during tests. Verify calls with `expect(dashboard.updateDom).toHaveBeenCalledWith(speed)`.

5. **jsdom is a devDependency** — already in `package.json`. The `// @vitest-environment jsdom` comment activates it per-file.

6. **Node_helper modules** — test pure functions separately (extract to `board-utils.js`-style files). The `NodeHelper.create()` wrapper is harder to mock; export the helper via `module.exports = _helper` and test exported functions.

## Running Tests

```bash
# All unit tests
npx vitest run tests/unit

# Specific module tests
npx vitest run tests/unit/modules/hermes-bridge/
npx vitest run tests/unit/modules/hermes-dashboard/hermes-dashboard_spec.js

# Watch mode during development
npx vitest watch tests/unit/modules/hermes-dashboard/
```

## Known Pre-existing Failure

1 test fails on macOS: `systeminfo expects "platform: linux"`. Not related to Hermes modules.
