# -*- coding: utf-8 -*-
import sys
from PySide6.QtCore import QSize, QRectF, QPointF, Qt
from PySide6.QtGui import QPainter, QPainterPath, QColor
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QLabel

# Matplotlib (no GUI backend needed here)
from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties
from matplotlib.path import Path as MplPath


class LatexWidget(QWidget):
    """
    QWidget that renders LaTeX (mathtext or usetex) as vector glyphs
    using Matplotlib's TextPath and paints them with QPainterPath.

    Parameters
    ----------
    text : str
        Input string. For mathtext, use $...$ (or set is_math=True to auto-wrap).
    font_family : str
        Matplotlib font family (e.g., "DejaVu Serif", "STIXGeneral").
    font_size_pt : float
        Font size in points.
    color : QColor | tuple | str
        Fill color for glyphs.
    is_math : bool
        If True, auto-wrap bare text in $...$.
    usetex : bool
        If True, use Matplotlib's full LaTeX engine (requires TeX installed).
    scale_mode : str
        "natural" (point-size at device DPI) or "fit" (scale to widget rect).
    padding_pt : float
        Padding around the content, in points (applies to "fit" mode and centering).
    """

    def __init__(
        self,
        text=r"$E=mc^2$",
        font_family="DejaVu Serif",
        font_size_pt=10.0,
        color=QColor("#222222"),
        is_math=True,
        usetex=False,
        scale_mode="natural",  # "natural" or "fit"
        padding_pt=4.0,
        parent=None,
    ):
        super().__init__(parent)

        # Stored properties
        self._text = text
        self._font_family = font_family
        self._font_size_pt = float(font_size_pt)
        self._color = QColor(color) if not isinstance(color, QColor) else color
        self._is_math = bool(is_math)
        self._usetex = bool(usetex)
        self._scale_mode = str(scale_mode).lower()
        self._padding_pt = float(padding_pt)

        if self._scale_mode not in ("natural", "fit"):
            raise ValueError('scale_mode must be "natural" or "fit"')

        # Cache: path in "point" units with +Y down to match Qt painter coordinates.
        self._path = QPainterPath()
        self._path_bounds_pt = QRectF()
        self._rebuild_path()

        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, True)
        self.setAutoFillBackground(False)

    # ------------- Public API -------------
    def setText(self, text: str):
        if text != self._text:
            self._text = text
            self._rebuild_path()
            self.updateGeometry()
            self.update()

    def text(self) -> str:
        return self._text

    def setFontFamily(self, family: str):
        if family != self._font_family:
            self._font_family = family
            self._rebuild_path()
            self.updateGeometry()
            self.update()

    def fontFamily(self) -> str:
        return self._font_family

    def setFontSizePt(self, size_pt: float):
        size_pt = float(size_pt)
        if size_pt > 0 and size_pt != self._font_size_pt:
            self._font_size_pt = size_pt
            self._rebuild_path()
            self.updateGeometry()
            self.update()

    def fontSizePt(self) -> float:
        return self._font_size_pt

    def setColor(self, color):
        new = QColor(color) if not isinstance(color, QColor) else color
        if new != self._color:
            self._color = new
            self.update()

    def color(self) -> QColor:
        return self._color

    def setIsMath(self, is_math: bool):
        is_math = bool(is_math)
        if is_math != self._is_math:
            self._is_math = is_math
            self._rebuild_path()
            self.updateGeometry()
            self.update()

    def isMath(self) -> bool:
        return self._is_math

    def setUseTeX(self, use_tex: bool):
        use_tex = bool(use_tex)
        if use_tex != self._usetex:
            self._usetex = use_tex
            self._rebuild_path()
            self.updateGeometry()
            self.update()

    def useTeX(self) -> bool:
        return self._usetex

    def setScaleMode(self, mode: str):
        mode = str(mode).lower()
        if mode not in ("natural", "fit"):
            raise ValueError('scale_mode must be "natural" or "fit"')
        if mode != self._scale_mode:
            self._scale_mode = mode
            self.updateGeometry()
            self.update()

    def scaleMode(self) -> str:
        return self._scale_mode

    def setPaddingPt(self, padding_pt: float):
        padding_pt = float(padding_pt)
        if padding_pt != self._padding_pt:
            self._padding_pt = padding_pt
            self.update()

    def paddingPt(self) -> float:
        return self._padding_pt

    # ------------- QWidget overrides -------------

    def sizeHint(self) -> QSize:
        """
        For 'natural' mode, suggest a size based on nominal 96 DPI.
        For 'fit', just return current size or a generic value.
        """
        if self._scale_mode == "fit":
            return super().sizeHint() or QSize(700, 180)

        nominal_dpi = 96
        base_scale = nominal_dpi / 72.0
        w_px = int((self._path_bounds_pt.width() + 2 * self._padding_pt) * base_scale)
        h_px = int((self._path_bounds_pt.height() + 2 * self._padding_pt) * base_scale)
        return QSize(max(1, w_px), max(1, h_px))

    def minimumSizeHint(self) -> QSize:
        return QSize(50, 30)

    def paintEvent(self, event):
        if self._path.isEmpty():
            return

        painter = QPainter(self)
        painter.setRenderHints(
            QPainter.Antialiasing | QPainter.TextAntialiasing | QPainter.SmoothPixmapTransform
        )

        # Convert points → pixels based on device DPI (typographic point = 1/72 inch)
        # Use X DPI as base; many displays have square pixels and same X/Y DPI.
        dpi_x = float(self.logicalDpiX())
        base_scale = dpi_x / 72.0

        w = float(self.width())
        h = float(self.height())

        # Bounds in "point" space
        bb = self._path_bounds_pt
        path_w_pt = bb.width() + 2 * self._padding_pt
        path_h_pt = bb.height() + 2 * self._padding_pt

        if self._scale_mode == "fit" and path_w_pt > 0 and path_h_pt > 0:
            # Additional scale beyond point-to-pixel to fit inside the widget
            scale_extra = min(
                w / (path_w_pt * base_scale),
                h / (path_h_pt * base_scale),
            )
        else:
            scale_extra = 1.0

        total_scale = base_scale * scale_extra
        painter.scale(total_scale, total_scale)

        # Work in "point" units from now on
        avail_w_pt = w / total_scale
        avail_h_pt = h / total_scale

        content_w_pt = bb.width()
        content_h_pt = bb.height()

        # Center inside available area with padding
        draw_w_pt = max(1e-6, avail_w_pt - 2 * self._padding_pt)
        draw_h_pt = max(1e-6, avail_h_pt - 2 * self._padding_pt)

        offset_x_pt = self._padding_pt + (draw_w_pt - content_w_pt) / 2.0 - bb.left()
        offset_y_pt = self._padding_pt + (draw_h_pt - content_h_pt) / 2.0 - bb.top()

        painter.translate(offset_x_pt, offset_y_pt)
        painter.setPen(Qt.NoPen)
        painter.setBrush(self._color)
        painter.drawPath(self._path)

    # ------------- Internals -------------

    def _ensure_math_wrapped(self, s: str) -> str:
        s = s.strip()
        if self._is_math:
            if not (s.startswith("$") and s.endswith("$")):
                s = f"${s}$"
        return s

    def _rebuild_path(self):
        """
        Builds QPainterPath from Matplotlib TextPath.
        The resulting path is in "point" units with Y axis inverted (+Y down) to match Qt.
        """
        s = self._ensure_math_wrapped(self._text)
        fp = FontProperties(family=self._font_family, size=self._font_size_pt)

        try:
            tp = TextPath(
                (0, 0),
                s,
                prop=fp,
                usetex=self._usetex,
                _interpolation_steps=1,
            )
        except Exception as e:
            # Fall back: display an error as simple vector rect text substitute
            self._path = QPainterPath()
            # Minimal placeholder box
            self._path.addRect(0, 0, 200, 40)
            self._path_bounds_pt = self._path.boundingRect()
            print(f"[LatexWidget] LaTeX render error: {e}")
            return

        verts = tp.vertices
        codes = tp.codes
        self._path = QPainterPath()

        def qt_point(v):
            # Invert Y to go from Matplotlib's Y-up to Qt's Y-down
            x, y = float(v[0]), float(v[1])
            return QPointF(x, -y)

        i = 0
        n = len(codes)
        while i < n:
            c = codes[i]
            v = verts[i]

            if c == MplPath.MOVETO:
                self._path.moveTo(qt_point(v))
                i += 1

            elif c == MplPath.LINETO:
                self._path.lineTo(qt_point(v))
                i += 1

            elif c == MplPath.CURVE3:
                # Quadratic: (control, end)
                if i + 1 < n:
                    cpt = qt_point(verts[i])
                    ept = qt_point(verts[i + 1])
                    self._path.quadTo(cpt, ept)
                    i += 2
                else:
                    break

            elif c == MplPath.CURVE4:
                # Cubic: (c1, c2, end)
                if i + 2 < n:
                    c1 = qt_point(verts[i])
                    c2 = qt_point(verts[i + 1])
                    ept = qt_point(verts[i + 2])
                    self._path.cubicTo(c1, c2, ept)
                    i += 3
                else:
                    break

            elif c == MplPath.CLOSEPOLY:
                self._path.closeSubpath()
                i += 1

            else:
                i += 1

        self._path_bounds_pt = self._path.boundingRect()
        # Trigger re-layout if in natural mode
        if self._scale_mode == "natural":
            self.updateGeometry()


# ---------------------------
# Minimal runnable demo window
# ---------------------------

class Demo(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LaTeX in QWidget via Matplotlib (vector glyphs)")

        self.latex = LatexWidget(
            text=r"\int_0^{\infty} e^{-x^2}\,dx = \frac{\sqrt{\pi}}{2}",
            font_family="STIXGeneral",   # try "DejaVu Serif" or "STIXGeneral"
            font_size_pt=28,
            color="#0b3d91",
            is_math=True,
            usetex=False,                # set True if you have LaTeX installed
            scale_mode="fit",            # "natural" or "fit"
            padding_pt=6.0,
        )

        self.input = QLineEdit(self.latex.text())
        self.input.setPlaceholderText(r'Enter LaTeX (mathtext), e.g. \frac{a}{b}')
        self.input.returnPressed.connect(self._apply_text)

        self.toggle_mode = QPushButton("Toggle scale mode (fit/natural)")
        self.toggle_mode.clicked.connect(self._toggle_scale_mode)

        top = QHBoxLayout()
        top.addWidget(QLabel("LaTeX:"))
        top.addWidget(self.input)
        top.addWidget(self.toggle_mode)

        layout = QVBoxLayout(self)
        layout.addLayout(top)
        layout.addWidget(self.latex, stretch=1)

        self.resize(900, 300)

    def _apply_text(self):
        self.latex.setText(self.input.text())

    def _toggle_scale_mode(self):
        mode = "natural" if self.latex.scaleMode() == "fit" else "fit"
        self.latex.setScaleMode(mode)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Demo()
    win.show()
    sys.exit(app.exec())
