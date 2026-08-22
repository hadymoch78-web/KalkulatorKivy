from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle
from kivy.core.window import Window
import ast
import operator


# Operasi yang diizinkan
OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
}


def hitung(expr):
    expr = expr.replace("×", "*").replace("÷", "/").replace(",", ".")

    try:
        tree = ast.parse(expr, mode="eval")

        def eval_node(node):
            if isinstance(node, ast.Expression):
                return eval_node(node.body)

            if isinstance(node, ast.Constant):
                if isinstance(node.value, (int, float)):
                    return node.value
                raise ValueError

            if isinstance(node, ast.BinOp):
                if type(node.op) not in OPS:
                    raise ValueError

                kiri = eval_node(node.left)
                kanan = eval_node(node.right)

                return OPS[type(node.op)](kiri, kanan)

            if isinstance(node, ast.UnaryOp):
                if isinstance(node.op, ast.USub):
                    return -eval_node(node.operand)
                if isinstance(node.op, ast.UAdd):
                    return eval_node(node.operand)

            raise ValueError

        hasil = eval_node(tree)

        if isinstance(hasil, float):
            if hasil.is_integer():
                return str(int(hasil))
            return f"{hasil:.10g}"

        return str(hasil)

    except Exception:
        return "Error"


class RoundButton(Button):
    def __init__(self, bg=(1, 1, 1, 1), **kwargs):
        super().__init__(**kwargs)

        self.background_normal = ""
        self.background_down = ""
        self.background_color = (0, 0, 0, 0)

        with self.canvas.before:
            Color(*bg)
            self.rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(22)]
            )

        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


class Calculator(BoxLayout):

    ORANGE = (1.0, 0.38, 0.02, 1)
    WHITE = (1, 1, 1, 1)
    BLACK = (0.05, 0.05, 0.05, 1)
    GRAY = (0.40, 0.40, 0.40, 1)

    def __init__(self, **kwargs):
        super().__init__(
            orientation="vertical",
            padding=[dp(12), dp(8), dp(12), dp(12)],
            spacing=dp(8),
            **kwargs
        )

        Window.clearcolor = (0.97, 0.97, 0.97, 1)

        self.expression = ""

        # =========================
        # HEADER
        # =========================
        header = BoxLayout(
            size_hint_y=None,
            height=dp(55),
            spacing=dp(10)
        )

        menu = Label(
            text="↙",
            font_size=dp(30),
            color=self.BLACK,
            size_hint_x=None,
            width=dp(50)
        )

        kalkulator = Label(
            text="Kalkulator",
            font_size=dp(22),
            color=self.BLACK
        )

        konverter = Label(
            text="Konverter",
            font_size=dp(22),
            color=self.GRAY
        )

        more = Label(
            text="⋮",
            font_size=dp(30),
            color=self.BLACK,
            size_hint_x=None,
            width=dp(35)
        )

        header.add_widget(menu)
        header.add_widget(kalkulator)
        header.add_widget(konverter)
        header.add_widget(more)

        self.add_widget(header)

        # =========================
        # DISPLAY
        # =========================
        display_box = BoxLayout(
            orientation="vertical",
            padding=[dp(10), dp(10)],
            spacing=dp(2)
        )

        self.display = Label(
            text="",
            font_size=dp(42),
            color=self.BLACK,
            halign="right",
            valign="bottom"
        )

        self.result = Label(
            text="",
            font_size=dp(24),
            color=self.GRAY,
            halign="right",
            valign="top"
        )

        self.display.bind(size=self.update_text_size)
        self.result.bind(size=self.update_text_size)

        display_box.add_widget(self.display)
        display_box.add_widget(self.result)

        self.add_widget(display_box)

        # =========================
        # BUTTON GRID
        # =========================
        grid = GridLayout(
            cols=4,
            rows=5,
            spacing=dp(10),
            size_hint_y=None
        )

        grid.bind(minimum_height=grid.setter("height"))

        buttons = [
            ("C", self.ORANGE),
            ("⌫", self.ORANGE),
            ("%", self.ORANGE),
            ("÷", self.ORANGE),

            ("7", self.BLACK),
            ("8", self.BLACK),
            ("9", self.BLACK),
            ("×", self.ORANGE),

            ("4", self.BLACK),
            ("5", self.BLACK),
            ("6", self.BLACK),
            ("−", self.ORANGE),

            ("1", self.BLACK),
            ("2", self.BLACK),
            ("3", self.BLACK),
            ("+", self.ORANGE),

            ("↔", self.ORANGE),
            ("0", self.BLACK),
            (",", self.BLACK),
            ("=", self.WHITE),
        ]

        for text, color in buttons:

            if text == "=":
                button = RoundButton(
                    bg=self.ORANGE,
                    text=text,
                    color=self.WHITE,
                    font_size=dp(30),
                    size_hint_y=None,
                    height=dp(82)
                )
            else:
                button = RoundButton(
                    bg=self.WHITE,
                    text=text,
                    color=color,
                    font_size=dp(28),
                    size_hint_y=None,
                    height=dp(82)
                )

            button.bind(on_release=self.button_pressed)
            grid.add_widget(button)

        self.add_widget(grid)

    def update_text_size(self, instance, value):
        instance.text_size = instance.size

    def button_pressed(self, button):
        key = button.text

        if key == "C":
            self.expression = ""
            self.display.text = ""
            self.result.text = ""
            return

        if key == "⌫":
            self.expression = self.expression[:-1]
            self.update_display()
            return

        if key == "=":
            if self.expression:
                hasil = hitung(self.expression)
                self.result.text = "= " + hasil

                if hasil != "Error":
                    self.expression = hasil
                    self.display.text = hasil
            return

        if key == "↔":
            return

        if key == "−":
            key = "-"

        if key == "×":
            key = "*"

        if key == "÷":
            key = "/"

        if key == ",":
            key = "."

        self.expression += key
        self.update_display()

    def update_display(self):
        tampil = self.expression
        tampil = tampil.replace("*", "×")
        tampil = tampil.replace("/", "÷")
        tampil = tampil.replace("-", "−")
        tampil = tampil.replace(".", ",")

        self.display.text = tampil

        if self.expression:
            hasil = hitung(self.expression)

            if hasil != "Error" and hasil != self.expression:
                self.result.text = "= " + hasil
            else:
                self.result.text = ""
        else:
            self.result.text = ""


class KalkulatorModernApp(App):

    def build(self):
        self.title = "Kalkulator Modern"
        return Calculator()


if __name__ == "__main__":
    KalkulatorModernApp().run()
