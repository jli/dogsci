import asyncio
from math import sin
from typing import Any, AsyncIterable, Optional

from rich.table import Table
from rich.text import Text
from textual.app import App
from textual import events
from textual.reactive import Reactive
from textual.layouts.grid import GridLayout
from textual.widget import Widget
from textual.widgets import (
    Header,
    Footer,
    Placeholder,
    FileClick,
    ScrollView,
    DirectoryTree,
)


async def stream_table_data() -> AsyncIterable[list[tuple[str, list[int]]]]:
    count = 0
    while True:
        rows: list[tuple[str, list[int]]] = []
        num_rows = 30 + round(sin(count / 5) * 9)
        for r in range(num_rows):
            row = []
            for c in range(8):
                row.append(count * r * c)
            rows.append((f"row {r}", row))
        yield rows
        await asyncio.sleep(2)
        count += 1


# async def main():
#     async for rows in stream_table_data():
#         print(rows)


# TODO: how do i update the outer scrollview from here when rows changes?
class StreamTable(Widget):
    rows: Reactive[list[tuple[str, list[Any]]]] = Reactive([])
    selected_row: Reactive[Optional[tuple[str, int]]] = Reactive(("row 2", 2))
    # hide_higlight = False

    def on_key(self, key_ev: events.Key):
        for (pair_num, ((name1, _), (name2, _))) in enumerate(
            zip(self.rows, self.rows[1:])
        ):
            if not self.selected_row:
                self.selected_row = (name1, pair_num)
                break
            if key_ev.key == "down" and name1 == self.selected_row[0]:
                self.selected_row = (name2, pair_num + 1)
                break
            elif key_ev.key == "up" and name2 == self.selected_row[0]:
                self.selected_row = (name1, pair_num)
                break
        else:
            if self.selected_row:
                _old_row_name, index = self.selected_row
                index = min(index, len(self.rows) - 1)
                cur_row_name_at_index, _values = self.rows[index]
                self.selected_row = (cur_row_name_at_index, index)

    def watch_rows(self, stuff):
        if (row := self.selected_row) and row[1] >= len(self.rows):
            new_index = min(row[1], len(self.rows) - 1)
            self.selected_row = (self.rows[new_index][0], new_index)

    def render(self) -> Table:
        table = Table(padding=0)
        columns_set = False
        for row_num, (row_name, row) in enumerate(self.rows):
            if not columns_set:
                for i, _ in enumerate(row, 1):
                    table.add_column(f"col {i}")
                columns_set = True
            if self.selected_row and (row_name == self.selected_row[0] or self.selected_row[1] >= len(self.rows)):
                row_rends = [Text(str(i), style="reverse") for i in row]
            else:
                row_rends = [str(i) for i in row]
            table.add_row(*row_rends)
        return table


class StreamTableApp(App):
    main: ScrollView
    table: StreamTable

    async def on_load(self) -> None:
        await self.bind("b", "view.toggle('sidebar')", "Toggle sidebar")
        await self.bind("q", "quit", "Quit")

    async def on_mount(self) -> None:
        # self.main = ScrollView()
        self.table = StreamTable()
        self.main = ScrollView(self.table)

        await self.view.dock(Header(), edge="top")
        await self.view.dock(Footer(), edge="bottom")
        await self.view.dock(Placeholder(), edge="left", size=20, name="sidebar")
        await self.view.dock(self.main, edge="top")

        asyncio.create_task(self.update_table())

    async def update_table(self):
        async for rows in stream_table_data():
            self.table.rows = rows


StreamTableApp.run(log="textual.log")
