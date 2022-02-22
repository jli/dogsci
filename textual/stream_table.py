import asyncio
from math import sin
from typing import Any, AsyncIterable, Literal, Optional, Union

from rich.table import Table
from rich.text import Text
from textual.app import App
from textual import events
from textual.message import Message
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


async def stream_table_data() -> AsyncIterable[list[list[str]]]:
    count = 0
    while True:
        rows: list[list[str]] = []
        num_rows = 30 + round(sin(count / 2) * 9)
        for r in range(num_rows):
            row = [f'row {r}']
            for c in range(8):
                row.append(str(count * r * c))
            rows.append(row)
        yield rows
        await asyncio.sleep(4)
        count += 1


# async def main():
#     async for rows in stream_table_data():
#         print(rows)

class ViewRowDetail(Message):
    row_name: str
    def __init__(self, sender, row_name: str):
        super().__init__(sender)
        self.row_name = row_name

class RowDetails(Widget):
    row_vals: list[str]

    def __init__(self, vals: list[str]):
        super().__init__()
        self.row_vals = vals

    def render(self) -> Text:
        # return Text.assemble(*(str(x) for x in self.row_vals))
        return Text('wtfffffffffffffff')


# TODO: how do i update the outer scrollview from here when rows changes?
class StreamTable(Widget):
    rows: Reactive[list[list[str]]] = Reactive([])
    selected_row: Reactive[Optional[tuple[str, int]]] = Reactive(("row 2", 2))
    # hide_higlight = False

    async def on_key(self, key_ev: events.Key):
        for (pair_num, (row1, row2)) in enumerate(
            zip(self.rows, self.rows[1:])
        ):
            name1 = row1[0]
            name2 = row2[0]
            if not self.selected_row:
                self.selected_row = (name1, pair_num)
                break
            # TODO: figure out how to handle scrolling the outer scrollview..
            if key_ev.key in ("down", "j") and name1 == self.selected_row[0]:
                self.selected_row = (name2, pair_num + 1)
                # key_ev.stop()
                break
            elif key_ev.key in ("up", "k") and name2 == self.selected_row[0]:
                self.selected_row = (name1, pair_num)
                # key_ev.stop()
                break
            elif key_ev.key in ("right", "l") and name1 == self.selected_row[0]:
                await self.emit(ViewRowDetail(self, name1))
                # self.rows[0][0] += 'TODO HAX'
                self.refresh(layout=True)
                break

    def watch_rows(self, stuff):
        if (row := self.selected_row) and row[1] >= len(self.rows):
            new_index = min(row[1], len(self.rows) - 1)
            self.selected_row = (self.rows[new_index][0], new_index)
        # needed to cause ScrollView container to update
        self.refresh(layout=True)

    def render(self) -> Table:
        table = Table(padding=0)
        columns_set = False
        for row in self.rows:
            row_name = row[0]
            if not columns_set:
                for i, _ in enumerate(row, 1):
                    table.add_column(f"col {i}")
                columns_set = True
            if self.selected_row and row_name == self.selected_row[0]:
                row_rends = [Text(str(i), style="reverse") for i in row]
            else:
                row_rends = [str(i) for i in row]
            table.add_row(*row_rends)
        return table


class StreamTableApp(App):
    header: Header
    main: ScrollView
    table: StreamTable
    row_details: RowDetails
    view_mode: Reactive[Union[Literal['table'], tuple[Literal['row'], str]]] = Reactive('table')

    async def on_load(self) -> None:
        await self.bind("b", "view.toggle('sidebar')", "Toggle sidebar")
        await self.bind("q", "quit", "Quit")

    async def on_mount(self) -> None:
        # self.main = ScrollView()
        self.table = StreamTable()
        # self.row_details =
        self.main = ScrollView(self.table)

        self.title = 'streamtable'
        self.header = Header(tall=False)
        await self.view.dock(self.header, edge="top")
        await self.view.dock(Footer(), edge="bottom")
        await self.view.dock(Placeholder(), edge="left", size=20, name="sidebar")
        await self.view.dock(self.main, edge="top")

        await self.table.focus()

        asyncio.create_task(self.update_table())

    async def watch_view_mode(self, blah):
        if self.view_mode == 'table':
            self.title = 'streamtable'
            await self.main.window.update(self.table)
        elif self.view_mode[0] == 'row':
            row_name = self.view_mode[1]
            matching = [r for r in self.table.rows if row_name == r[0]]
            row = matching[0]
            self.row_details = RowDetails(row)
            await self.main.window.update(self.row_details)
            self.title = f'streamtable > {row_name}'
            # self.table.rows[0][0] += 'wtfff'

    def on_key(self, key_ev: events.Key):
        if self.view_mode != 'table' and key_ev.key in ('left', 'h'):
            self.view_mode = 'table'

    def handle_view_row_detail(self, detail: ViewRowDetail):
        # self.table.rows[0][0] += 'parent'
        self.view_mode = ('row', detail.row_name)

    def handle_back_to_table(self):
        self.view_mode = 'table'

    async def update_table(self):
        async for rows in stream_table_data():
            self.table.rows = rows


StreamTableApp.run(log="textual.log")
