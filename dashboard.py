# coding=utf-8

import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import json


######################################
# styling
######################################
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
colors = {
    'background': '#ffd8ab',
    'text': '#000000'
}
style = {
    'textAlign': 'center',
    'color': colors['text'],
    'background-color': colors["background"]
}
choropleth_style = {'margin': '0'}

plotly_template = "plotly"

######################################
# Data
######################################

url = "https://www.arcgis.com/sharing/rest/content/items/b5e7488e117749c19881cce45db13f7e/data"
# if url == None:
dfs = pd.read_excel(url, sheet_name=None, index_col=False)
# else:
#    dfs = pd.read_excel("data/Folkhalsomyndigheten_Covid19.xlsx", sheet_name=None, index_col=False)

info = dfs[list(dfs.keys())[-1]].iloc[0, 0]

df_total_per_region = dfs["Totalt antal per region"]
df_total_per_region["Fall_per_100000_inv"] = df_total_per_region["Fall_per_100000_inv"].round(0)
df_antal_avlidna_per_dag = dfs["Antal avlidna per dag"]
df_antal_intensiv_per_dag = dfs["Antal intensivvårdade per dag"]
df_totalt_antal_per_koen = dfs["Totalt antal per kön"]
df_total_per_aldersgrupp = dfs["Totalt antal per åldersgrupp"]
df_antal_per_dag_region = dfs["Antal per dag region"]

with open(r'data/sweden.geojson') as f:
    geojson = json.load(f)

######################################
# Graphs config
######################################
config = {'displaylogo': False, "displayModeBar": False, "scrollZoom": False,
          'locale': 'se', 'staticPlot': False}

######################################
# generate_choropleth
######################################
def generate_choropleth(data):
    figure = px.choropleth(df_total_per_region, geojson=geojson, color=data,
                           locations="Region", featureidkey="properties.name_short",
                           projection="mercator", color_continuous_scale="Reds", labels={data: " "},
                           hover_name="Region", hover_data={'Region': False},
                           template=plotly_template
                           )
    figure.update_geos(fitbounds="locations", visible=False)
    figure.update_layout(geo=dict(bgcolor='rgba(0,0,0,0)'), font=dict(color="black", size=15), showlegend=True)
    figure.update_layout(margin={"r": 0, "t": 25, "l": 0, "b": 0}, autosize=True,
                         plot_bgcolor='rgba(0, 0, 0, 0)', paper_bgcolor='rgba(0, 0, 0, 0)')
    return figure


######################################
# make_dropdown
######################################
def make_dropdown(options):
    dropdown = list()
    for option in options:
        di = {'label': option, 'value': option}
        dropdown.append(di)
    return dropdown


######################################
# generate_region_graph
######################################
def generate_region_graph(region):
    region_data = df_total_per_region.loc[df_total_per_region["Region"] == region]

    figure = px.bar(region_data,
                    y=['Totalt antal fall',
                       'Fall per 100000 inv',
                       'Totalt antal intensivvårdade',
                       'Totalt antal avlidna'],
                    x=[region_data['Totalt_antal_fall'].values[0], region_data['Fall_per_100000_inv'].values[0],
                       region_data['Totalt_antal_intensivvårdade'].values[0],
                       region_data['Totalt_antal_avlidna'].values[0]], orientation='h', template=plotly_template
                    )
    figure.update_layout(title=" ", xaxis_title=" ", yaxis_title=" ", autosize=True,
                          plot_bgcolor='rgba(0, 0, 0, 0)', paper_bgcolor='rgba(0, 0, 0, 0)',
                         font=dict(size=15))
    figure.update_traces(marker_color=['red'] * 4, showlegend=False)
    return figure


totalt_antal_avlidna = df_total_per_region['Totalt_antal_avlidna'].sum()
totalt_antal_intensiv = df_total_per_region['Totalt_antal_intensivvårdade'].sum()
totalt_antal_fall = df_total_per_region['Totalt_antal_fall'].sum()


######################################
# create_layout
######################################
def create_layout():
    return html.Div([
        html.Div([
            html.H1('Covid-19 Statistik Sverige'),
            html.H3(children="Totalt antal avlidna: " + str(totalt_antal_avlidna), className="text-top"),
            html.H3(children="Totalt antal fall: " + str(totalt_antal_fall), className="text-top"),
            html.H3(children="Totalt antal intensivårdade: " + str(totalt_antal_intensiv), className="text-top"),
            html.Div([
                html.Div([
                    html.H3("Avlidna"),
                    dcc.Graph(figure=generate_choropleth("Totalt_antal_avlidna"),
                              style=choropleth_style, config=config),
                ], className="six columns"),

                html.Div([
                    html.H3("Intensivvårdade"),
                    dcc.Graph(figure=generate_choropleth("Totalt_antal_intensivvårdade"),
                              style=choropleth_style, config=config)
                ], className="six columns"),
            ], className="row"),
            html.Div([
                html.Div([
                    html.H3("Antal Fall"),
                    dcc.Graph(figure=generate_choropleth("Totalt_antal_fall"),
                              style=choropleth_style, config=config)
                ], className="six columns"),

                html.Div([
                    html.H3("Fall Per 100 000 invånare"),
                    dcc.Graph(figure=generate_choropleth("Fall_per_100000_inv"),
                              style=choropleth_style, config=config)
                ], className="six columns"),
            ], className="row"),

            # dcc.RangeSlider(marks=df_total_per_region["Region"].to_dict()),
            # dcc.Dropdown(options=make_dropdown(df_total_per_region["Region"]), multi=True),
            html.Div([
                html.Div([
                html.H3("Välj region för detaljerad statistik"),
                dcc.Dropdown(id="region_input", options=make_dropdown(df_total_per_region["Region"]), value="Stockholm",
                             clearable=False, searchable=False,
                             className="region-dropdown")
            ], className="text-top"),
                dcc.Graph(id="region_output", figure=generate_region_graph("Stockholm"), config=config,
                          style={'margin': '0 auto'}, className="region-graph")
            ], className="container"),
            html.Footer(children=info, style={'margin': 'left 100px right 100px top 300px', 'font-size': '11px'},
                        className="bottom-text")
        ], className="container", )
    ], style=style)


######################################
# layout
######################################
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = 'Sverige - Covid-19 Dashboard'
server = app.server

app.layout = create_layout()


# Change region chart
@app.callback(Output(component_id="region_output", component_property="figure"),
              [Input(component_id="region_input", component_property="value")])
def update_region_figure(selected_region):
    return generate_region_graph(selected_region)


if __name__ == '__main__':
    app.run_server(debug=True)

    # todo add multiple regions to chart, group by region
    # todo fix styling
    # todo dark mode
    # todo timeline
    # todo tables
    # todo related news
    # todo age groups
    # todo drag mode
    # reduce size