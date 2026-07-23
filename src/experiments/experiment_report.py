"""Relatório HTML autocontido para uma execução experimental concluída"""

from __future__ import annotations

from collections import Counter
from html import escape
import json
import math
from pathlib import Path
from statistics import median
from typing import Iterable, Sequence

ACTION_NAMES = (
    "FRONT_CLOCKWISE",
    "FRONT_COUNTERCLOCKWISE",
    "REAR_CLOCKWISE",
    "REAR_COUNTERCLOCKWISE",
)
SHORT_ACTION_NAMES = ("Front CW", "Front CCW", "Rear CW", "Rear CCW")
SERIES_COLORS = ("var(--n0)", "var(--n1)", "var(--n2)", "var(--n3)")


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_iterations(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _fmt(value: float, digits: int = 3) -> str:
    if abs(value) < 10 ** (-(digits + 1)) and value != 0:
        return f"{value:.2e}"
    return f"{value:.{digits}f}"


def _polyline_points(
    values: Sequence[float], width: float, height: float, minimum: float, maximum: float
) -> str:
    span = maximum - minimum or 1.0
    denominator = max(len(values) - 1, 1)
    return " ".join(
        f"{index * width / denominator:.1f},{height - (value - minimum) * height / span:.1f}"
        for index, value in enumerate(values)
    )


def _line_chart(
    *,
    title: str,
    series: Sequence[tuple[str, Sequence[float], str]],
    y_label: str,
    fixed_range: tuple[float, float] | None = None,
) -> str:
    width, height = 960.0, 250.0
    plot_x, plot_y, plot_w, plot_h = 72.0, 20.0, 864.0, 180.0
    all_values = [value for _, values, _ in series for value in values]
    if not all_values:
        return ""
    minimum, maximum = fixed_range or (min(all_values), max(all_values))
    if math.isclose(minimum, maximum):
        padding = max(abs(minimum) * 0.1, 1.0)
        minimum, maximum = minimum - padding, maximum + padding
    grid = []
    for index in range(5):
        y = plot_y + index * plot_h / 4
        value = maximum - index * (maximum - minimum) / 4
        grid.append(
            f'<line x1="{plot_x}" y1="{y:.1f}" x2="{plot_x + plot_w}" y2="{y:.1f}" class="grid"/>'
            f'<text x="{plot_x - 10}" y="{y + 4:.1f}" text-anchor="end">{escape(_fmt(value))}</text>'
        )
    lines = []
    for label, values, color in series:
        points = _polyline_points(values, plot_w, plot_h, minimum, maximum)
        lines.append(
            f'<polyline points="{points}" transform="translate({plot_x} {plot_y})" '
            f'style="stroke:{color}" class="series-line"><title>{escape(label)}</title></polyline>'
        )
    legend = "".join(
        f'<span><i style="background:{color}"></i>{escape(label)}</span>'
        for label, _, color in series
    )
    last_iteration = max(len(values) for _, values, _ in series) - 1
    return f"""
    <section>
      <h2>{escape(title)}</h2>
      <div class="legend">{legend}</div>
      <svg class="chart" viewBox="0 0 {width:.0f} {height:.0f}" role="img" aria-label="{escape(title)}">
        <title>{escape(title)}</title>
        {''.join(grid)}
        <line x1="{plot_x}" y1="{plot_y + plot_h}" x2="{plot_x + plot_w}" y2="{plot_y + plot_h}" class="axis"/>
        {''.join(lines)}
        <text x="{plot_x}" y="230">0</text>
        <text x="{plot_x + plot_w}" y="230" text-anchor="end">{last_iteration}</text>
        <text x="{plot_x + plot_w / 2}" y="246" text-anchor="middle">Iteração</text>
        <text x="16" y="{plot_y + plot_h / 2}" text-anchor="middle" transform="rotate(-90 16 {plot_y + plot_h / 2})">{escape(y_label)}</text>
      </svg>
    </section>"""


def _timeline(rows: Sequence[dict]) -> str:
    width, height = 960.0, 126.0
    left, usable = 72.0, 864.0
    cell = usable / max(len(rows), 1)
    action_marks = []
    direction_marks = []
    direction_color = {
        "DOWN": "var(--down)",
        "UP": "var(--up)",
        "STATIONARY": "var(--stationary)",
    }
    for index, row in enumerate(rows):
        x = left + index * cell
        action = int(row["previous_action"])
        action_marks.append(
            f'<rect x="{x:.2f}" y="24" width="{max(cell + .2, .6):.2f}" height="28" '
            f'style="fill:{SERIES_COLORS[action]}"><title>Iteração {index}: {ACTION_NAMES[action]}</title></rect>'
        )
        direction = row["direction"]
        direction_marks.append(
            f'<rect x="{x:.2f}" y="68" width="{max(cell + .2, .6):.2f}" height="28" '
            f'style="fill:{direction_color[direction]}"><title>Iteração {index}: {direction}</title></rect>'
        )
    return f"""
    <section>
      <h2>Linha do tempo</h2>
      <div class="legend">
        {''.join(f'<span><i style="background:{SERIES_COLORS[i]}"></i>{SHORT_ACTION_NAMES[i]}</span>' for i in range(4))}
        <span><i style="background:var(--down)"></i>Descida</span>
        <span><i style="background:var(--stationary)"></i>Parado</span>
        <span><i style="background:var(--up)"></i>Subida</span>
      </div>
      <svg class="chart" viewBox="0 0 {width:.0f} {height:.0f}" role="img" aria-label="Ações e direções por iteração">
        <title>Ações e direções por iteração</title>
        <text x="64" y="43" text-anchor="end">Ação</text>
        <text x="64" y="87" text-anchor="end">Direção</text>
        {''.join(action_marks)}{''.join(direction_marks)}
        <text x="{left}" y="116">0</text>
        <text x="{left + usable}" y="116" text-anchor="end">{max(len(rows) - 1, 0)}</text>
      </svg>
    </section>"""


def _network_diagram(rows: Sequence[dict]) -> tuple[str, str]:
    first = rows[0]["neural_step"]
    last = rows[-1]["neural_step"]
    initial = first["weights_before"]
    final = last["weights_after"]
    shifts = last["shifts_after"]
    wins = Counter(int(row["neural_step"]["winner"]) for row in rows)
    positions = ((300, 70), (520, 230), (300, 390), (80, 230))

    candidates = []
    for target in range(4):
        for source in range(4):
            if source == target:
                continue
            delta = final[target][source] - initial[target][source]
            candidates.append(
                (abs(delta), final[target][source], source, target, delta)
            )
    changed = [item for item in candidates if item[0] > 1e-10]
    selected = changed[:]
    for item in sorted(candidates, key=lambda value: value[1], reverse=True):
        if item not in selected:
            selected.append(item)
        if len(selected) >= 8:
            break

    edges = []
    for _, weight, source, target, delta in selected:
        x1, y1 = positions[source]
        x2, y2 = positions[target]
        dx, dy = x2 - x1, y2 - y1
        length = math.hypot(dx, dy)
        ux, uy = dx / length, dy / length
        sx, sy = x1 + ux * 53, y1 + uy * 53
        ex, ey = x2 - ux * 58, y2 - uy * 58
        bend = 22 if source < target else -22
        mx, my = (sx + ex) / 2 - uy * bend, (sy + ey) / 2 + ux * bend
        label_x, label_y = mx - uy * 7, my + ux * 7
        edge_class = "edge changed" if abs(delta) > 1e-10 else "edge"
        edges.append(
            f'<path d="M {sx:.1f} {sy:.1f} Q {mx:.1f} {my:.1f} {ex:.1f} {ey:.1f}" '
            f'class="{edge_class}" style="stroke-width:{1 + 4 * min(abs(weight), 1):.2f}" marker-end="url(#arrow)">'
            f"<title>{SHORT_ACTION_NAMES[source]} → {SHORT_ACTION_NAMES[target]}: peso {weight:.4f}, Δ {delta:+.4f}</title></path>"
            f'<text x="{label_x:.1f}" y="{label_y:.1f}" text-anchor="middle" class="edge-label">{weight:.3f}</text>'
        )

    nodes = []
    for index, (x, y) in enumerate(positions):
        nodes.append(
            f'<g class="node" transform="translate({x} {y})">'
            f'<circle r="52" style="fill:{SERIES_COLORS[index]}"/>'
            f'<text y="-15" text-anchor="middle" class="node-title">N{index + 1}</text>'
            f'<text y="5" text-anchor="middle">{SHORT_ACTION_NAMES[index]}</text>'
            f'<text y="24" text-anchor="middle">wins {wins[index]} · shift {shifts[index]:.3f}</text>'
            f'<text y="41" text-anchor="middle">self {final[index][index]:.3f}</text>'
            f"</g>"
        )

    diagram = f"""
    <section>
      <h2>Rede neural treinada</h2>
      <p class="caption">As setas mostram conexões <strong>origem → destino</strong>. A espessura representa o peso final; linhas destacadas mudaram durante o treinamento. O número junto à seta é o peso final. Para manter a leitura, são exibidas as conexões alteradas e as mais fortes; a matriz abaixo contém todas.</p>
      <svg class="network" viewBox="0 0 600 470" role="img" aria-label="Diagrama final da rede neural de quatro neurônios">
        <title>Rede neural treinada</title>
        <defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" class="arrow"/></marker></defs>
        {''.join(edges)}{''.join(nodes)}
      </svg>
    </section>"""

    header = "".join(f"<th>{escape(SHORT_ACTION_NAMES[i])}</th>" for i in range(4))
    body = []
    for target in range(4):
        cells = []
        for source in range(4):
            delta = final[target][source] - initial[target][source]
            cells.append(
                f'<td class="num"><strong>{final[target][source]:.4f}</strong><br><span class="muted">Δ {delta:+.4f}</span></td>'
            )
        body.append(
            f"<tr><th>{escape(SHORT_ACTION_NAMES[target])}</th>{''.join(cells)}</tr>"
        )
    matrix = f"""
    <section>
      <h2>Matriz final de pesos</h2>
      <p class="caption">Colunas são neurônios de origem; linhas são neurônios de destino. Cada célula mostra peso final e variação desde a inicialização.</p>
      <div class="table-wrap"><table><thead><tr><th>Destino ↓ / origem →</th>{header}</tr></thead><tbody>{''.join(body)}</tbody></table></div>
    </section>"""
    return diagram, matrix


def _longest_run(rows: Sequence[dict]) -> tuple[int, int, int, int]:
    best_action = best_start = best_end = best_length = 0
    start = 0
    for index in range(1, len(rows) + 1):
        if (
            index == len(rows)
            or rows[index]["previous_action"] != rows[start]["previous_action"]
        ):
            length = index - start
            if length > best_length:
                best_action = int(rows[start]["previous_action"])
                best_start, best_end, best_length = start, index - 1, length
            start = index
    return best_action, best_start, best_end, best_length


def _analysis(rows: Sequence[dict], summary: dict) -> tuple[dict, list[str]]:
    directions = Counter(row["direction"] for row in rows)
    downward = directions["DOWN"]
    stationary = directions["STATIONARY"]
    upward = directions["UP"]
    gaps = []
    saturated = 0
    exact_ties = 0
    for row in rows:
        outputs = sorted(row["neural_step"]["raw_output"], reverse=True)
        gaps.append(outputs[0] - outputs[1])
        saturated += all(value >= 0.999 for value in outputs)
        exact_ties += outputs[0] == outputs[1]
    action, start, end, length = _longest_run(rows)
    learning = summary.get("learning", {})
    historical = learning.get(
        "everDownwardCriterionReached",
        any(row["learning"].get("downward_criterion_reached", False) for row in rows),
    )
    first_criterion = learning.get("firstDownwardCriterionIteration")
    if first_criterion is None:
        first_criterion = next(
            (
                row["iteration"]
                for row in rows
                if row["learning"].get("downward_criterion_reached")
            ),
            None,
        )
    metrics = {
        "iterations": len(rows),
        "down": downward,
        "stationary": stationary,
        "up": upward,
        "productive": downward / len(rows) if rows else 0.0,
        "saturation": saturated / len(rows) if rows else 0.0,
        "saturated_count": saturated,
        "ties": exact_ties,
        "median_gap": median(gaps) if gaps else 0.0,
        "historical": historical,
        "first_criterion": first_criterion,
    }
    notes = [
        f"A execução terminou por {summary.get('reason', 'motivo não registrado')} após {len(rows)} iterações; {downward} ({metrics['productive']:.1%}) produziram aproximação da meta.",
        (
            f"O critério de descidas consecutivas foi alcançado pela primeira vez na iteração {first_criterion}."
            if historical
            else "O critério de descidas consecutivas não foi alcançado nesta execução."
        ),
        f"A maior repetição de uma ação durou {length} ciclos: {ACTION_NAMES[action]}, das iterações {start} a {end}.",
        f"As quatro saídas ficaram simultaneamente ≥ 0,999 em {saturated} ciclos ({metrics['saturation']:.1%}); ocorreram {exact_ties} empates exatos no topo.",
    ]
    if stationary + upward > downward:
        notes.append(
            f"Ciclos improdutivos predominaram: {stationary} estacionários e {upward} para cima, contra {downward} para baixo."
        )
    if metrics["saturation"] >= 0.25:
        notes.append(
            "A saturação é alta e reduz a capacidade da competição de distinguir os neurônios; examine os gráficos de saídas, shifts e entradas sensoriais no mesmo intervalo."
        )
    return metrics, notes


def generate_experiment_report(run_directory: str | Path) -> Path:
    """Gera ``report.html`` usando somente os artefatos persistidos da execução."""

    directory = Path(run_directory)
    metadata = _load_json(directory / "metadata.json")
    summary = _load_json(directory / "summary.json")
    rows = _load_iterations(directory / "iterations.jsonl")
    if not rows:
        raise ValueError("cannot generate a report without iterations")

    metrics, notes = _analysis(rows, summary)
    runtime = metadata.get(
        "runtimeConfig", metadata.get("config", {}).get("runtime", {})
    )
    action_duration = float(runtime.get("action_duration_seconds", 0.5))
    cumulative = []
    total = 0.0
    for row in rows:
        total -= float(row["displacement"])
        cumulative.append(total)
    accelerations = [float(row["sensory_input"]["acceleration"]) for row in rows]
    sounds = [float(row["sensory_input"]["sound"]) for row in rows]
    raw_outputs = [
        [float(row["neural_step"]["raw_output"][index]) for row in rows]
        for index in range(4)
    ]
    shifts = [
        [float(row["neural_step"]["shifts_after"][index]) for row in rows]
        for index in range(4)
    ]
    network, matrix = _network_diagram(rows)

    action_rows = []
    for action in range(4):
        selected = [row for row in rows if int(row["previous_action"]) == action]
        counts = Counter(row["direction"] for row in selected)
        mean_displacement = (
            sum(float(row["displacement"]) for row in selected) / len(selected)
            if selected
            else 0.0
        )
        action_rows.append(
            f'<tr><th>{escape(ACTION_NAMES[action])}</th><td class="num">{len(selected)}</td>'
            f"<td class=\"num\">{counts['DOWN']}</td><td class=\"num\">{counts['STATIONARY']}</td>"
            f"<td class=\"num\">{counts['UP']}</td><td class=\"num\">{mean_displacement:.6f}</td></tr>"
        )

    config_rows = []
    for label, value in (
        ("Seed", runtime.get("random_seed", "—")),
        ("Duração por ação", f"{action_duration:g} s"),
        ("Velocidade das rodas", runtime.get("wheel_speed", "—")),
        ("Intensidade da maraca", runtime.get("sound_intensity", "—")),
        ("Escala da aceleração", runtime.get("acceleration_scale", "—")),
    ):
        config_rows.append(
            f"<tr><th>{escape(label)}</th><td>{escape(str(value))}</td></tr>"
        )

    report = f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Relatório experimental — {escape(directory.name)}</title>
<style>
:root{{--bg:#f7f8fa;--surface:#fff;--text:#18202b;--muted:#5c6878;--border:#d8dee8;--grid:#dfe4ec;--n0:#2878b5;--n1:#d98024;--n2:#2e9666;--n3:#8a5bb3;--down:#2e9666;--stationary:#8993a1;--up:#c44747;--changed:#d98024}}
@media(prefers-color-scheme:dark){{:root{{--bg:#11151b;--surface:#191f28;--text:#edf2f7;--muted:#aab4c2;--border:#35404f;--grid:#303947;--n0:#60a9dc;--n1:#eda75e;--n2:#62c493;--n3:#b88bd7;--down:#62c493;--stationary:#8793a3;--up:#e27676;--changed:#eda75e}}}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--bg);color:var(--text);font:15px/1.5 system-ui,-apple-system,Segoe UI,sans-serif}} main{{max-width:1120px;margin:auto;padding:32px 24px 64px}} h1{{font-size:28px;margin:0 0 4px}} h2{{font-size:19px;margin:34px 0 10px}} p{{margin:6px 0}} .muted,.caption{{color:var(--muted)}} .cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin:24px 0}} .card{{background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:14px}} .card span{{display:block;color:var(--muted)}} .card strong{{display:block;font-size:24px;font-weight:500;margin-top:3px}} .status{{font-weight:500}} ul{{padding-left:22px}} li{{margin:7px 0}} section{{border-top:1px solid var(--border);margin-top:28px;padding-top:1px}} .chart,.network{{display:block;width:100%;height:auto;color:var(--text)}} .chart text,.network text{{fill:var(--text);font-size:12px}} .grid{{stroke:var(--grid);stroke-width:1}} .axis{{stroke:var(--muted);stroke-width:1}} .series-line{{fill:none;stroke-width:2}} .legend{{display:flex;gap:13px;flex-wrap:wrap;color:var(--muted);font-size:13px;margin-bottom:4px}} .legend span{{white-space:nowrap}} .legend i{{display:inline-block;width:11px;height:11px;border-radius:3px;margin-right:5px}} table{{border-collapse:collapse;width:100%}} th,td{{padding:9px 10px;text-align:left;border-bottom:1px solid var(--border)}} thead th{{color:var(--muted);font-weight:500}} tbody th{{font-weight:500}} .num{{text-align:right;font-variant-numeric:tabular-nums}} .table-wrap{{overflow-x:auto}} .network{{max-width:760px;margin:auto}} .edge{{fill:none;stroke:var(--muted);opacity:.48}} .edge.changed{{stroke:var(--changed);opacity:.9}} .arrow{{fill:var(--muted)}} .edge-label{{paint-order:stroke;stroke:var(--bg);stroke-width:4px;stroke-linejoin:round}} .node circle{{fill-opacity:.22;stroke:var(--border);stroke-width:1.5}} .node text{{font-size:11px}} .node .node-title{{font-size:16px;font-weight:500}} footer{{color:var(--muted);margin-top:40px;border-top:1px solid var(--border);padding-top:16px}} @media(max-width:600px){{main{{padding:22px 12px 48px}}h1{{font-size:22px}}th,td{{padding:7px}}}}
</style></head><body><main>
<header><h1>Relatório do experimento neural</h1><p class="muted"><code>{escape(directory.name)}</code> · gerado automaticamente a partir dos arquivos da execução</p></header>
<div class="cards">
  <div class="card"><span>Resultado</span><strong>{escape(summary.get('reason', '—'))}</strong></div>
  <div class="card"><span>Iterações / tempo</span><strong>{metrics['iterations']} / {metrics['iterations'] * action_duration:.1f}s</strong></div>
  <div class="card"><span>Descidas produtivas</span><strong>{metrics['down']} ({metrics['productive']:.1%})</strong></div>
  <div class="card"><span>Critério histórico</span><strong>{'Sim' if metrics['historical'] else 'Não'}</strong></div>
  <div class="card"><span>Saturação conjunta</span><strong>{metrics['saturated_count']} ({metrics['saturation']:.1%})</strong></div>
</div>
<section><h2>Leitura automática</h2><ul>{''.join(f'<li>{escape(note)}</li>' for note in notes)}</ul></section>
{_timeline(rows)}
{_line_chart(title='Progresso acumulado em direção à meta',series=(('Progresso',cumulative,'var(--down)'),),y_label='Metros')}
{_line_chart(title='Entradas sensoriais',series=(('Aceleração',accelerations,'var(--n0)'),('Maraca',sounds,'var(--n1)')),y_label='Entrada normalizada')}
{_line_chart(title='Saídas brutas dos neurônios',series=tuple((f'N{i + 1} · {SHORT_ACTION_NAMES[i]}',raw_outputs[i],SERIES_COLORS[i]) for i in range(4)),y_label='Saída',fixed_range=(0.0,1.0))}
{_line_chart(title='Shifts intrínsecos',series=tuple((f'N{i + 1} · {SHORT_ACTION_NAMES[i]}',shifts[i],SERIES_COLORS[i]) for i in range(4)),y_label='Shift')}
<section><h2>Eficiência das ações</h2><div class="table-wrap"><table><thead><tr><th>Ação</th><th class="num">Ciclos</th><th class="num">Down</th><th class="num">Parado</th><th class="num">Up</th><th class="num">Deslocamento médio</th></tr></thead><tbody>{''.join(action_rows)}</tbody></table></div></section>
{network}{matrix}
<section><h2>Configuração registrada</h2><table><tbody>{''.join(config_rows)}</tbody></table></section>
<footer>Fonte: <code>metadata.json</code>, <code>iterations.jsonl</code> e <code>summary.json</code>. Pesos usam a convenção publicada e implementada <code>w[target][source]</code>, isto é, conexão source → target.</footer>
</main></body></html>"""
    destination = directory / "report.html"
    destination.write_text(report, encoding="utf-8", newline="\n")
    return destination
