# Canvas (Skia Graphics)

Talon provides a Canvas API built on Skia for drawing overlays, widgets, and visual feedback.

## Entry Points

```python
from talon import canvas, ui, screen, skia
from talon.ui import Rect, Point2d
```

## Creating a Canvas

```python
# Full-screen canvas
c = canvas.Canvas.from_screen(ui.main_screen())

# Positioned canvas
c = canvas.Canvas.from_rect(Rect(100, 100, 400, 300))
```

**Windows Bug**: Apply height fix for `from_screen`:
```python
if app.platform == "windows":
    rect = Rect(*screen.rect)
    rect.height -= 1
    c.rect = rect
```

## Canvas Lifecycle

The canvas uses a freeze/resume pattern:

```python
def draw(c):
    paint = c.paint
    paint.color = "#FF0000"
    c.draw_rect(Rect(10, 10, 100, 50))

# Create and draw
canvas_obj = canvas.Canvas.from_screen(ui.main_screen())
canvas_obj.focusable = False
canvas_obj.register("draw", draw)
canvas_obj.freeze()  # Triggers draw, then freezes

# Update later
canvas_obj.resume()
canvas_obj.freeze()  # Redraws

# Cleanup
canvas_obj.unregister("draw", draw)
canvas_obj.close()
```

## Drawing Basics

Inside the draw callback, you receive a `skia.Canvas`:

```python
def draw(c):
    paint = c.paint

    # Colors
    paint.color = "#FF0000"       # Red
    paint.color = "#FF000088"     # Red, 50% transparent

    # Style
    paint.style = paint.Style.FILL      # Filled
    paint.style = paint.Style.STROKE    # Outline only
    paint.stroke_width = 2

    # Shapes
    c.draw_rect(Rect(10, 10, 100, 50))
    c.draw_circle(200, 50, 25)
    c.draw_line(50, 100, 150, 150)
    c.draw_round_rect(Rect(10, 100, 100, 50), 8, 8)

    # Text
    paint.textsize = 16
    c.draw_text("Hello", 10, 200)
```

## Paint Properties

| Property | Description |
|----------|-------------|
| `color` | Fill/stroke color |
| `style` | FILL, STROKE, or STROKE_AND_FILL |
| `stroke_width` | Line width |
| `textsize` | Font size |
| `typeface` | Font name |
| `antialias` | Enable antialiasing |

### Text Measurement

```python
width, bounds = paint.measure_text("Hello World")
# width = advance width
# bounds = Rect with bounding box (bounds.y is negative = above baseline)
```

## Paths

For complex shapes:

```python
path = skia.Path()
path.move_to(0, 0)
path.line_to(100, 0)
path.line_to(50, 100)
path.close()
c.draw_path(path)

# Load from SVG
path = skia.Path.from_svg("M 0 0 L 100 0 L 50 100 Z")
```

## Transforms

```python
c.save()
c.translate(100, 100)
c.rotate_degrees(45)
c.scale(2, 2)
c.draw_rect(Rect(-25, -25, 50, 50))
c.restore()

# Or use context manager
with c.saved():
    c.translate(100, 100)
    c.draw_circle(0, 0, 20)
```

## Clipping

```python
c.save()
c.clip_rect(Rect(50, 50, 100, 100))
# Drawing is now restricted to this rect
c.draw_rect(Rect(0, 0, 200, 200))  # Only visible inside clip
c.restore()
```

## Gradients

```python
shader = skia.Shader.linear_gradient(
    start=(0, 0),
    end=(100, 0),
    colors=["#FF0000", "#0000FF"]
)
paint.shader = shader
c.draw_rect(Rect(0, 0, 100, 100))
paint.shader = None  # Reset
```

## Canvas Properties

| Property | Description |
|----------|-------------|
| `rect` | Position and size |
| `focusable` | Can receive keyboard focus |
| `draggable` | User can drag window |
| `blocks_mouse` | Receives mouse events |
| `title` | Window title |

## Events

```python
c.register("draw", on_draw)
c.register("click", on_click)       # Mouse click
c.register("mouse", on_mouse)       # Mouse move (requires blocks_mouse=True)
c.register("key", on_key)           # Key press (requires focus)
```

## Screen Capture

```python
from talon import screen

img = screen.capture(x, y, width, height)
img.save("screenshot.png")
```

## Offscreen Rendering

```python
surface = skia.Surface(200, 200)
surf_canvas = surface.canvas()
# Draw to surface...
img = surface.snapshot()
surface.write_file("output.png")
```

## Multi-Screen

```python
for scr in ui.screens():
    c = canvas.Canvas.from_screen(scr)
    # ...
```

## Detailed Reference

See `settings/api_exploration/canvas/CANVAS_API_EXPLORATION.md` for complete API documentation including:
- All paint properties and methods
- Font metrics and text wrapping
- Complete path API (arcs, curves, SVG interop)
- All gradient types (linear, radial, sweep, conical)
- Image loading and manipulation
- Blend modes (29 modes)
- API limitations (what's not available)
- Test file index
