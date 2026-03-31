from __future__ import annotations

from template.app.gui.presenters.main_presenter import MainPresenter
from template.infrastructure.startup import bootstrap


def run(argv: list[str] | None = None) -> int:
    _ = argv
    from template.app.gui.views.main_view import MainView

    presenter = MainPresenter(bootstrap())
    view = MainView(presenter)
    presenter.bind(view)
    view.mainloop()
    return 0
