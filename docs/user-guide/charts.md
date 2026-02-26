# Historical Charts

The **Charts** page lets you visualise the historical values of one or more Modbus variables over any time range, with optional aggregation.

---

## Selecting variables and time range

1. Go to **Charts**.
2. Click the **Configure** button to open the query form.
3. The form has three parts:

### Part 1 — Variable selection

A modal (identical in layout to the Dashboard modal) lists your assigned devices and their variables. Check the variables you want to include in the chart.


### Part 2 — Date and time range

Use the **start** and **end** date-time pickers to define the query window.

| Picker | Purpose |
|---|---|
| **Start** | Earliest timestamp to include (inclusive). |
| **End** | Latest timestamp to include (inclusive). |

### Part 3 — Aggregation

Choose how the raw readings are grouped before display:

| Option | Label | Result |
|---|---|---|
| `sin` | **No aggregation** | Every individual reading is plotted as-is. Best for short time ranges. |
| `horas` | **By hours** | Values within each clock-hour are averaged. Smooths hourly trends. |
| `dias` | **By days** | Values within each calendar day are averaged. Best for long time ranges. |


1. Click **Submit** (or **Apply**) to execute the query.

---

## Reading the chart

The result is rendered as a Highcharts interactive line chart. Each selected variable appears as a coloured line series.


Interactive features:

| Feature | How to use |
|---|---|
| **Tooltip** | Hover over any data point to see the exact value and timestamp. |
| **Zoom** | Click and drag on the chart area to zoom in on a time range. |
| **Pan** | After zooming, click and drag with the pan tool (if enabled). |
| **Reset zoom** | Click the **Reset zoom** button that appears after zooming. |
| **Legends** | Click a series name in the legend to show or hide that series. |

---

## Exporting the chart

The Highcharts export menu (≡ or hamburger icon in the top-right corner of the chart) provides several download options:

| Format | Notes |
|---|---|
| **PNG** | Raster image at screen resolution. |
| **SVG** | Vector image suitable for publications. |
| **PDF** | Print-ready document containing the chart. |
| **CSV** | Raw data table with timestamps and values. |
| **XLS** | Spreadsheet-compatible format. |

Click the desired format; the browser downloads the file immediately.
