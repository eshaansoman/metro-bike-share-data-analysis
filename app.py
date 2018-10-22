import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
import plotly.plotly as py
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State

#CSS stylesheet from the given link.
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css'] 
#This adds the stylesheet to our web application
app = dash.Dash(__name__, external_stylesheets=external_stylesheets) 
 #This helps with deployment of the web application
server = app.server

#This reads the csv file and turns it into a dataframe.
raw_bikeshare_data = pd.read_csv('metro-bike-share-trip-data.csv', low_memory=False)
# Station 4108 does not have accurate longitude and latitude coordinates, so it must be removed to produce reliable results.
raw_bikeshare_data_omitting_station_4108 = raw_bikeshare_data[(
    raw_bikeshare_data['Starting Station ID'] != 4108) & (raw_bikeshare_data['Ending Station ID'] != 4108)]
# This creates a dataframe that has a column for every Starting Station ID and a column for the number of rides that started from each station.
starting_station_count = pd.DataFrame(
    {"count": raw_bikeshare_data.groupby(["Starting Station ID"]).size()}).reset_index()
# This creates a dataframe has a column for every Ending Station ID and a column for the number of rides that ended at each station.
ending_station_count = pd.DataFrame(
    {"count": raw_bikeshare_data.groupby(["Ending Station ID"]).size()}).reset_index()
# This creates a dataframe that has a row for every unique Station Station to Ending Station route and counts the number of times each route was taken.
start_to_end_station_trip_count = pd.DataFrame({"count": raw_bikeshare_data.groupby(
    ["Starting Station ID", "Ending Station ID"]).size()}).reset_index()
# This adds the column "Starting to Ending Station Trip" to the "start_to_end_station_trip_count" data that combines the Starting Station ID and Ending Station ID into one column, so a graph is easier to make.
start_to_end_station_trip_count["Starting to Ending Station Trip"] = start_to_end_station_trip_count["Starting Station ID"].astype(
    str) + " to " + start_to_end_station_trip_count["Ending Station ID"].astype(str).map(str)
# This creates a dataframe that only contains information for round trips
round_trips_only = raw_bikeshare_data[raw_bikeshare_data["Trip Route Category"]
                            == "Round Trip"]
# This creates a dataframe that contains the number of round trips that leave from each Starting Station ID.
round_trips_by_starting_starting_station = pd.DataFrame(
    {"count": round_trips_only.groupby(["Starting Station ID"]).size()}).reset_index()
# This creates a dataframe that only contains information for one-way trips
one_way_trips_only = raw_bikeshare_data[raw_bikeshare_data["Trip Route Category"] == "One Way"]
# This creates a dataframe that contains the number of one-way trips that leave from each Starting Station ID.
one_way_trips_by_starting_starting_station = pd.DataFrame(
    {"count": one_way_trips_only.groupby(["Starting Station ID"]).size()}).reset_index()
# This creates a dataframe that has a column for passholder types and another column for the number of rides taken using each passholder type.
passholder_type_count = pd.DataFrame(
    {"count": raw_bikeshare_data.groupby(["Passholder Type"]).size()}).reset_index()
# This creates a dataframe that has a column for trip route categories and another column for the number of rides for each trip route.
trip_route_category_count = pd.DataFrame(
    {"count": raw_bikeshare_data.groupby(["Trip Route Category"]).size()}).reset_index()
# This creates a dataframe that has a rwo for every unique Passholder Type and Trip Route combination and counts the numbers of rides for each times each combination.
trip_route_passholder_type_combo_count = pd.DataFrame({"count": raw_bikeshare_data.groupby(
    ["Passholder Type", "Trip Route Category"]).size()}).reset_index()
# This adds the columnn "Passholder Type & Trip Route" to the "trip_route_passholder_type_combo_count" data that combines the Passholder Type and Trip Route Category into one column, so a graph is easier to make.
trip_route_passholder_type_combo_count["Passholder Type & Trip Route"] = trip_route_passholder_type_combo_count[
    "Passholder Type"] + " & " + trip_route_passholder_type_combo_count["Trip Route Category"].map(str)
# This creates a dataframe that splits the "Start Time" column in the "raw_bikeshare_data" dataframe and creates two new columns "Starting Date" and "Starting Time"
raw_bikeshare_data_split_starting_date_and_time = raw_bikeshare_data.join(raw_bikeshare_data["Start Time"].str.split(
    "T", expand=True)).rename(columns={0: "Starting Date", 1: "Starting Time"})
# This creates a dataframe that has a column "Starting Date" and a column that counts the number of rides for each day.
number_of_rides_per_day = pd.DataFrame(
    {"count": raw_bikeshare_data_split_starting_date_and_time.groupby(["Starting Date"]).size()}).reset_index()
# This creates a dataframe that contains the number of rides taken using the different Passholder types for each day.
passholder_type_count_by_day = pd.DataFrame({"count": raw_bikeshare_data_split_starting_date_and_time.groupby([
    "Starting Date", "Passholder Type"]).size()}).reset_index()
# This creates a dataframe that contains the the number of rides taken each day using the Flex Pass
flex_pass_count_by_day = passholder_type_count_by_day[
    passholder_type_count_by_day["Passholder Type"] == "Flex Pass"]
# This creates a dataframe that contains the number of rides taken each day using the Monthly Pass
monthly_pass_count_by_day = passholder_type_count_by_day[
    passholder_type_count_by_day["Passholder Type"] == "Monthly Pass"]
# This creates a dataframe that contains the number of rides taken each day using Walk-ups.
walk_up_count_by_day = passholder_type_count_by_day[
    passholder_type_count_by_day["Passholder Type"] == "Walk-up"]
# This creates a dataframe that contains the number of rides taken each day using the Staff Annual passholder type.
staff_annual_count_by_day = passholder_type_count_by_day[
    passholder_type_count_by_day["Passholder Type"] == "Staff Annual"]
# This creates a dataframe that contains the number of rides taken for each Trip Route Category for each day.
trip_route_count_by_day = pd.DataFrame({"count": raw_bikeshare_data_split_starting_date_and_time.groupby(
    ["Starting Date", "Trip Route Category"]).size()}).reset_index()
# This creates a dataframe that contains the number of one-way rides per day.
one_way_count_by_day = trip_route_count_by_day[
    trip_route_count_by_day["Trip Route Category"] == "One Way"]
# This creates a dataframe that contains the number of round trip rides per day.
round_trip_count_by_day = trip_route_count_by_day[
    trip_route_count_by_day["Trip Route Category"] == "Round Trip"]
# This returns the median duration of rides in minutes
median_duration_of_rides_in_minutes = np.median(raw_bikeshare_data["Duration"])/60
# This returns the mean duration of rides in minutes
average_duration_of_rides_in_minutes = np.mean(raw_bikeshare_data["Duration"])/60
# This creates a dataframe that contains only round trips, exlcuding those that start and end at Station 4108, since the longitude and latitude are incorrect for that station.
round_trips_only = raw_bikeshare_data[raw_bikeshare_data["Trip Route Category"]
                            == "Round Trip"]
# This creates a dataframe that contains only one-way trips, exlcuding those that start or end at Station 4108, since the longitude and latitude are incorrect for that station.
one_way_trips_only = raw_bikeshare_data_omitting_station_4108[
    raw_bikeshare_data_omitting_station_4108["Trip Route Category"] == "One Way"]
# This changes all coordinates from degrees to radians. We are only using one-way trips because the starting and ending stations have different coordinates.
starting_longitude, starting_latitude, ending_longitude, ending_latitude = map(
    np.radians, [one_way_trips_only['Starting Station Longitude'], one_way_trips_only['Starting Station Latitude'], one_way_trips_only['Ending Station Longitude'], one_way_trips_only['Ending Station Latitude']])
# This calculates the difference between the starting and ending latitudes
difference_of_latitudes = ending_latitude - starting_latitude
# This calculates the difference between the starting and ending longitudes.
difference_of_longitudes = ending_longitude - starting_longitude
# This is the Haversine distance formula for calculating distance between a set of coordinates.
r = 3959  #radius of Earth in miles
distance_in_miles = 2 * 3959 * np.arcsin(np.sqrt((np.sin(difference_of_latitudes/2))**2 + np.cos(
    starting_latitude) * np.cos(ending_latitude) * (np.sin(difference_of_longitudes/2))**2))
# This adds a column "Distance in Miles" containing the distance traveled for each one-way ride to the "one_way_trips_only" dataframe.
one_way_trips_only["Distance in Miles"] = pd.Series(
    distance_in_miles).values
# This makes sure that each distance is above 0, so we know we don't have any null values or faulty data.
one_way_trips_only_with_distance = one_way_trips_only[one_way_trips_only["Distance in Miles"] > 0]
# This calculates average speed in miles per minutes for one-way trips.
average_speed_in_miles_per_min = np.sum(
    one_way_trips_only_with_distance["Distance in Miles"])/np.sum(one_way_trips_only_with_distance["Duration"]/60)
# This estimates the distance traveled during round trips by multiplying the average speed of the one-way trips by the durations of the round-trips. We are assuming that the average speed of the one-way trips is the average speed for all trips.
estimate_distances_for_round_trips = average_speed_in_miles_per_min * \
    (round_trips_only["Duration"]/60)
# This adds a column "Estimated Distance in Miles" containing the estimated distance traveled for each round trip ride to the "round_trips_only" dataframe.
round_trips_only["Estimated Distance in Miles"] = pd.Series(
    estimate_distances_for_round_trips).values
# This makes sure that each distance is above 0, so we know we don't have any null values or faulty data.
round_trips_only_with_estimated_distance = round_trips_only[
    round_trips_only["Estimated Distance in Miles"] > 0]
# This calculates an estimate for the average distance traveled by riders.  
average_distance = (one_way_trips_only_with_distance["Distance in Miles"].sum() + round_trips_only_with_estimated_distance["Estimated Distance in Miles"].sum())/(len(one_way_trips_only_with_distance["Distance in Miles"]) + len(
    round_trips_only_with_estimated_distance["Estimated Distance in Miles"]))  
# This creates a dataframe that has the column "Starting Date" and a column "Average Duration" with the average duration of rides for each day in minutes.
average_ride_duration_by_day = (raw_bikeshare_data_split_starting_date_and_time[["Starting Date", "Duration"]].groupby(
    ["Starting Date"]).mean()/60).reset_index().rename(columns={'Duration': 'Average Duration'})
# This creates a dataframe that contains the number of rides that started every minute.
number_of_rides_by_time = pd.DataFrame(
    {"count": raw_bikeshare_data_split_starting_date_and_time.groupby(["Starting Time"]).size()}).reset_index()

app.layout = html.Div([
    dcc.Tabs(id="tabs", children=[
        dcc.Tab(label="Welcome Page", children=[
             html.Div([
                 html.H1(
                      'Welcome!',
                      style={
                          'textAlign': 'center',
                          'marginTop': 25
                      }
                      ),
                 html.Div('''
                        The Metro Bike Share system offers convenient access to bicycles for both short and long trips 24 hours a day, 365 days a year. This web application analyzes and visualizes the data from The Metro Bike Share system from the city of Los Angeles.
                            ''',
                          style={
                              'textAlign': 'center',
                              'fontSize': 24,
                              'marginLeft': 25,
                              'marginRight': 25
                          }
                          ),
                 dcc.Graph(
                     id="map",
                     figure={
                         "data": [
                             go.Scattermapbox(
                                 lat=raw_bikeshare_data_omitting_station_4108["Starting Station Latitude"],
                                 lon=raw_bikeshare_data_omitting_station_4108["Starting Station Longitude"],
                                 mode="markers",
                                 marker=dict(
                                      size=5,
                                      color="yellow"
                                 ),
                                 text=raw_bikeshare_data["Starting Station ID"],
                                 hoverinfo="text"
                             )
                         ],

                         'layout': go.Layout(
                             title="The map belowed shows the location of all the metro bike stations. Each location is labeled by its Station ID number.",
                             autosize=True,
                             hovermode='closest',
                             mapbox=dict(
                                 # This is a public access key from mapbox.com
                                 accesstoken='pk.eyJ1IjoiZXNoYWFuc29tYW4iLCJhIjoiY2puZTZydnJuNjZyejN4bjFueWR1em16cyJ9.KIip4vcOMeBAJVMSL81-JA',
                                 bearing=0,
                                 center=dict(
                                     lat=34.0441589,
                                     lon=-118.25158
                                 ),
                                 pitch=0,
                                 zoom=11.8,
                                 style='dark'
                             )
                         )
                     }
                 ),
             ])
             ]),
        dcc.Tab(label='Station Information', children=[
            html.Div([
                dcc.Graph(
                      id='starting-station',
                      figure={
                          'data': [
                              go.Bar(
                                  x=starting_station_count["Starting Station ID"],
                                  y=starting_station_count["count"],
                                  marker=dict(
                                      color='#DE425B'
                                  )
                              )
                          ],
                          'layout': go.Layout(
                              title="Starting Station Frequencies",
                              xaxis=dict(
                                  title="Starting Station ID",
                                  # This range covers all of the Starting Station IDs except for Station 4108. To view data for Station 4108, doulbe click on the graph.
                                  range=[2999, 3083]
                              ),
                              yaxis=dict(
                                  range=[0, 6500]
                              )
                          )
                      }
                ),
                html.Div('''
                        This bar graph shows the number of trips that leave from each starting station. The most popular starting station is Station 3069, with 5,138 rides leaving from there! The least popular starting station is Station 3009. This is because the station is located in Venice, Los Angeles, which is extrmeely far away from the cluster of ride stations in downtown LA.
                            ''',
                         style={
                             'textAlign': 'center',
                             'marginRight': 25,
                             'marginLeft': 25
                         }
                         ),
                dcc.Graph(
                    id='ending-station',
                    figure={
                        'data': [
                            go.Bar(
                                x=ending_station_count["Ending Station ID"],
                                y=ending_station_count["count"],
                                marker=dict(
                                    color='#488F31'
                                )
                            )
                        ],
                        'layout': go.Layout(
                            title="Ending Station Frequencies",
                            xaxis=dict(
                                title="Ending Station ID",
                                # This range covers all of the Ending Station IDs except for Station 4108. To view data for Station 4108, doulbe click on the graph.
                                range=[2999, 3083]
                            ),
                            yaxis=dict(
                                range=[0, 6500]
                            )
                        )
                    }
                ),
                html.Div('''
                            This bar graph shows the number of trips that end at each station. It is clear that the most popular destination is Station 3005, with 6,262 rides ending there! Again, we see that the least number of rides end at Station 3009, because the station is so far away from the rest.
                            ''',
                         style={
                             'textAlign': 'center',
                             'marginRight': 25,
                             'marginLeft': 25
                         }
                         ),
                dcc.Graph(
                    id="start-to-end-station-trip-count",
                    figure={
                        'data': [
                            go.Bar(
                                x=start_to_end_station_trip_count["Starting to Ending Station Trip"],
                                y=start_to_end_station_trip_count["count"],
                                marker=dict(
                                    color='#003F5C'
                                )

                            )
                        ],
                        'layout': go.Layout(
                            title="Starting to Ending Station Trips",
                            xaxis=dict(
                                title="Start to End Stations",
                                tickfont=dict(
                                    size=5
                                )
                            ),
                            yaxis=dict(
                                title="Number of Rides",
                                range=(0, 1000)
                            ),
                        )
                    }
                ),
                html.Div('''
                        This bar graph shows the number of trips taken from a specific starting station to a specific ending station. Going from Station 3030 to Station 3014 is the most popular path; it has been traveled 933 times!
                            ''',
                         style={
                             'textAlign': 'center',
                             'marginRight': 25,
                             'marginLeft': 25
                         }
                         ),
                dcc.Graph(
                    id='type-of-rides-from-start-station',
                    figure={
                        'data': [
                            go.Bar(
                                x=round_trips_by_starting_starting_station["Starting Station ID"],
                                y=round_trips_by_starting_starting_station["count"],
                                name="Round Trips",
                                marker=dict(
                                    color='#E1D35B'
                                )
                            ),
                            go.Bar(
                                x=one_way_trips_by_starting_starting_station["Starting Station ID"],
                                y=one_way_trips_by_starting_starting_station["count"],
                                name="One-Way Trips",
                                marker=dict(
                                    color='#E69554'
                                )
                            )
                        ],
                        'layout': go.Layout(
                            barmode='group',
                            title="Type of Rides at Starting Stations",
                            xaxis=dict(
                                title="Starting Station ID",
                                # This range covers all of the Starting Station IDs except for Station 4108. To view data for Station 4108, doulbe click on the graph.
                                range=[2999, 3083]
                            ),
                            yaxis=dict(
                                title="Number of Rides",
                                range=[0, 5000]
                            )
                        )
                    }
                ),
                html.Div('''
                        The graphs above shows the number of round-trip and one-way rides that leave from each station.
                          ''',
                         style={
                             'textAlign': 'center',
                             'marginRight': 25,
                             'marginLeft': 25,
                             'marginBottom': 25
                         }
                         )
            ])
        ]),
        dcc.Tab(label='Passholder Types & Trip Routes', children=[
            html.Div([
                dcc.Graph(
                      id='passholder-type-count',
                      figure={
                          'data': [
                              go.Pie(
                                  labels=passholder_type_count["Passholder Type"],
                                  values=passholder_type_count["count"],
                                  hoverinfo='percent+value',
                                  textinfo='label',
                                  textfont=dict(size=14),
                                  domain={
                                      # This centers the pie chart with respect to the others in the tab.
                                      'x': [0.3, 0.7],
                                      'y': [0, 1]
                                  },
                                  marker=dict(
                                      colors=['#5DA5DA', '#60BD68',
                                              '#DECF3F ', '#FFA600']
                                  )
                              )
                          ],
                          'layout': go.Layout(
                              title="Passholder Types Breakdown",
                          )
                      }
                ),
                html.Div('''
                          The pie chart above shows the breakdown of the number of rides taken by different passholder types. It is evident that the Monthly Pass is the most popular (accounting for 61.4 perecent of all rides). Many people most probably feel comfortable purchasing a Monthly Pass, since it is not a long time commitment like the Flex Pass, and is still cheaper than buying Walk-ups. We can assume that riders who go out of their way to purchase a bike pass will use the pass regularly. Therefore, it is safe to assume that all Monthly Pass and Flex Pass holders include bike sharing as a regular part of their commute. This is also confirmed by the weekly pattern of passholder types seen in the "Ridership Change with Seasons" tab.
                        ''',
                         style={
                             'textAlign': 'center',
                             'marginRight': 25,
                             'marginLeft': 25
                         }
                         ),
                dcc.Graph(
                    id='trip-route-category-count',
                    figure={
                        'data': [
                            go.Pie(
                                labels=trip_route_category_count["Trip Route Category"],
                                values=trip_route_category_count["count"],
                                hoverinfo='percent+value',
                                textinfo='label',
                                textfont=dict(size=14),
                                domain={
                                    # This centers the pie chart with respect to the others in the tab.
                                    'x': [0.3, 0.7],
                                    'y': [0, 1]
                                },
                                marker=dict(
                                    colors=['#BC5090', '#FF6361']
                                )
                            )
                        ],
                        'layout': go.Layout(
                            title="Trip Route Breakdown",
                        )
                    }
                ),
                html.Div('''
                          The pie chart above shows the breakdown of one-way trips and round-trips. The overwhemlingly majority (90.3%) of trips are one-way. A small portion (9.65%) constitutes of round-trips. Since a lot of people use this system to commute, they most likely make a one-way trip to work and another one-way trip back home. This explains why so many of the trips are one-way.
                          ''',
                         style={
                             'textAlign': 'center',
                             'marginRight': 25,
                             'marginLeft': 25

                         }
                         ),
                dcc.Graph(
                    id='trip-route-passholder-type-combo',
                    figure={
                        'data': [
                            go.Pie(
                                labels=trip_route_passholder_type_combo_count[
                                    "Passholder Type & Trip Route"],
                                values=trip_route_passholder_type_combo_count["count"],
                                hoverinfo='percent+value',
                                textinfo='label',
                                domain={
                                    # This centers the pie chart with respect to the others in the tab.
                                    'x': [0.35, 0.75],
                                    'y': [0, 1]
                                }
                            )
                        ],
                        'layout': go.Layout(
                            title="Trip Route & Passholder Types Combinations",
                        )
                    }
                ),
                html.Div('''
                          The pie chart above shows the breakdown of Trip Route Category and Passholder type combinations. Most trips were taken by Monthly Pass holders and were one-way. This combination is the most popular because monthly passes provide the perfect balance of a short term-time commitment and a good value for the money spent. Similarly, most trips are one-way because people take a one-way trip to their destination, and another one-way trip back. Thus, the combination of a Monthly Pass and one-way trip is the most popular, as seen through this pie chart.
                            ''',
                         style={
                             'textAlign': 'center',
                             'marginBottom': 25,
                             'marginLeft': 25,
                             'marginRight': 25
                         }
                         ),
            ])
        ]),
        dcc.Tab(label="Duration & Distance", children=[
            html.Div([
                dcc.Graph(
                      id='ride-duration-distribution',
                      figure={
                          'data': [
                              go.Histogram(
                                  x=raw_bikeshare_data["Duration"]/60,
                                  marker=dict(
                                      color='#D5BA4F'
                                  )
                              )
                          ],
                          'layout': go.Layout(
                              title="Ride Duration Distribution",
                              xaxis=dict(
                                  title="Ride Duration (in minutes)",
                                  range=(0, 90)
                              ),
                              yaxis=dict(
                                  title=("Number of Rides")
                              )
                          )
                      }
                ),
                html.Div('''
                          The graph above shows the distribution of the duration of rides. The histogram is postively skewed, meaning the distribution has a 'long tail' on the positive side of the peak. We see that the number of rides decrease after thirty minutes; this is because for passholders, there is a fee for every minute after a 30 minute ride. The median ride time is {} minutes, while the the average ride time is {} minutes. The mode duration of trips is between 6-7 minutes.
                          '''.format(median_duration_of_rides_in_minutes, round(average_duration_of_rides_in_minutes, 2)),
                         style={
                    'textAlign': 'center',
                    'marginLeft': 25,
                    'marginRight': 25
                }
                ),
                dcc.Graph(
                    id='one-way-distances-traveled',
                    figure={
                        'data': [
                            go.Histogram(
                                name="One-Way Trip Dist.",
                                x=one_way_trips_only_with_distance["Distance in Miles"],
                                nbinsx=400,
                                marker=dict(
                                    color='#58985E'
                                )
                            )
                        ],
                        'layout': go.Layout(
                            title="One-Way Ride Distance Distribution",
                            xaxis=dict(
                                  title="Distance Traveled (in miles)",
                                  range=(0, 4)
                            ),
                            yaxis=dict(
                                title=("Number of Rides")
                            )
                        )
                    }
                ),
                html.Div('''
                          This histogram shows the distribution for the distance traveled during one-way trips. This distribution is also positively skewed. The distance was calculated by using the latitude and longitude coordinates of the starting and ending stations. The mode distance for one way trips is between 0.45 and 0.5 a mile. The majority of one-way trips are between 0.05 and 2 miles.
                            ''',
                         style={
                             'textAlign': 'center',
                             'marginLeft': 25,
                             'marginRight': 25
                         }
                         ),
                dcc.Graph(
                    id='round-trip-estimated-distances-traveled',
                    figure={
                        'data': [
                            go.Histogram(
                                name="Round-Trip Estimated Dist.",
                                x=round_trips_only_with_estimated_distance[
                                    "Estimated Distance in Miles"],
                                nbinsx=1200,
                                marker=dict(
                                    color='#15504F'
                                )
                            )
                        ],
                        'layout': go.Layout(
                            title="Estimated Round Trip Distance Distribution",
                            xaxis=dict(
                                  title="Estimated Distance Traveled (in miles)",
                                  range=(0, 4)
                            ),
                            yaxis=dict(
                                title=("Number of Rides")
                            )
                        )
                    }
                ),
                html.Div('''
                          This histogram shows the distribution of the estimated distance traveled during round trips. The distance cannot be calculated precisely using latitude and longitude coordinates, because the starting and ending stations are the same for round trips. By calculating the average speed of bike rides (using data from one-way trips), and multiplying it by the duration of each round trip ride, we are able to find a rough estimate for the distance of each round trip ride. We see that the peak in the estimated distance for round trips occurs around 0.85-90 miles, which is double the distance where the peak for one-way trips occured. This makes sense because round-trip rides are usually about twice as long as one-way rides.
                            ''',
                         style={
                             'textAlign': 'center',
                             'marginLeft': 25,
                             'marginRight': 25
                         }
                         ),
                html.Div("The average distance traveled is ~{} miles".format(round(average_distance, 3)),
                         style={
                    'textAlign': 'center',
                    'fontSize': 40,
                    'marginTop': 25,
                    'marginLeft': 25,
                    'marginRight': 25,
                    'marginBottom': 25
                }
                ),
            ])
        ]),
        dcc.Tab(label='Ridership Change with Seasons', children=[
            html.Div([
                dcc.Graph(
                      id="number-of-rides-per-day",
                      figure={
                          'data': [
                              go.Scatter(
                                  x=number_of_rides_per_day["Starting Date"],
                                  y=number_of_rides_per_day["count"],
                                  mode="lines",
                                  marker=dict(
                                      color='#990000'
                                  )
                              )
                          ],
                          'layout': go.Layout(
                              title="Total Number of Rides Per Day",
                              yaxis=dict(
                                  title="Total Number of Rides"
                              )
                          )
                      }
                ),
                html.Div('''
                          This graph shows the number of rides per day over a course of 9 months. We can see that in the summer months (July & August), the number of rides per day increases over time. Starting the fall season in September, the number of rides per day decreases all the way until the end of winter (end of February). This makes sense because as weather gets colder, people are less inclined to ride bikes. During the spring, we see a slow increase in the total number of rides per day, since the weather warms up and people like spending more time outside. One interesting observation is the sudden spike in ridership on October 16, 2016, which is odd for the seasonal pattern. This is a result of the CicLAvia Bike Festival hosted in downtown LA on that day. Similarly, we see another odd spike in ride on January 21, 2017; this can be attributed to 2018 LA Women's March, where people where encouraged to use Bike Share instead of cars because of traffic.
                            ''',
                         style={
                             'textAlign': 'center',
                             'marginLeft': 25,
                             'marginRight': 25
                         }
                         ),
                dcc.Graph(
                    id="passholder-type-count-by-day",
                    figure={
                        'data': [
                            go.Scatter(
                                x=flex_pass_count_by_day["Starting Date"],
                                y=flex_pass_count_by_day["count"],
                                mode="lines",
                                name="Flex Pass",
                                marker=dict(
                                    color='#D9CE58'
                                )
                            ),
                            go.Scatter(
                                x=monthly_pass_count_by_day["Starting Date"],
                                y=monthly_pass_count_by_day["count"],
                                mode="lines",
                                name="Monthly Pass",
                                marker=dict(
                                    color='#3B9E80'
                                )
                            ),
                            go.Scatter(
                                x=walk_up_count_by_day["Starting Date"],
                                y=walk_up_count_by_day["count"],
                                mode="lines",
                                name="Walk-up",
                                marker=dict(
                                    color='#A8617A'
                                )
                            ),
                            go.Scatter(
                                x=staff_annual_count_by_day["Starting Date"],
                                y=staff_annual_count_by_day["count"],
                                name="Staff Annual",
                                marker=dict(
                                    color='#DE7D60'
                                )
                            )
                        ],
                        'layout': go.Layout(
                            title="Passholder Types by Day",
                            yaxis=dict(
                                title="Total Number of Rides"
                            )
                        )
                    }
                ),
                html.Div('''
                          The graph above shows the number of rides taken per day by different passholder types over the course of 9 months. Again, the number of rides for all four different types of passholders is heightened during the summer months, dips during the winter months, and slowly starts to increase again during the spring. We see an immense spike of Walk-ups on October 16, 2016, since people bought these one-time passes for the CicLAvia Bike Festival. A similar spike in Walk-ups is observed on January 21, 2017, because of the LA Women's March. Another fascinating aspect of the graph is that the rides taken using the Monthly and Flex Passes significantly dips every weekend, while the number of rides taken with the Walk-up pass spikes. This can be attributed to the fact that many people who have the Monthly or Flex Pass use it as part of their daily commute to work on the weekdays; on the weekends, people do not have work, so ridership using the Monthly and Flex Pass drops. On the other hand, the number of rides using the Walk-up pass increases drastically on the weekends, because people like tourists often visit L.A on the weekend, and use the Walk-Up pass as a fun mode of transportation.
                            ''',
                         style={
                             'textAlign': 'center',
                             'marginLeft': 25,
                             'marginRight': 25
                         }
                         ),
                dcc.Graph(
                    id="trip-type-count-by-day",
                    figure={
                        'data': [
                            go.Scatter(
                                x=one_way_count_by_day["Starting Date"],
                                y=one_way_count_by_day["count"],
                                mode="lines",
                                name="One-Way",
                                marker=dict(
                                    color='#4F9D6B'
                                )
                            ),
                            go.Scatter(
                                x=round_trip_count_by_day["Starting Date"],
                                y=round_trip_count_by_day["count"],
                                mode="lines",
                                name="Round Trip",
                                marker=dict(
                                    color='#20533D'
                                )
                            )
                        ],
                        'layout': go.Layout(
                            title="Trip Route Types by Day",
                            yaxis=dict(
                                title="Total Number of Rides"
                            )
                        )
                    }
                ),
                html.Div('''
                          The graph above shows the number of Round Trip and One-Way rides taken per day. The number of Round-Trip rides stay relatively constant over the seasons, but dips slightly in the winter. The number of One-Way trips follows the pattern we saw in the other graphs: a spike during the summer months, a low during the winter months, and an incline starting during the spring. Round Trips also spike every weekend, while One-Way trips drop. This is because many people use One-Way trips to commute; so on the weekends when there is no work, less one-way trips occur. On the other hand, Round trips increase because people go biking on the weekends as a fun outdoors activity and usually return to the same destination afterwards.
                            ''',
                         style={
                             'textAlign': 'center',
                         }
                         ),
                dcc.Graph(
                    id="average-trip-duration-by-day",
                    figure={
                        'data': [
                            go.Scatter(
                                x=average_ride_duration_by_day["Starting Date"],
                                y=average_ride_duration_by_day["Average Duration"],
                                mode="lines",
                                marker=dict(
                                    color='#856A8F'
                                )
                            )
                        ],
                        'layout': go.Layout(
                            title="Average Trip Duration By Day",
                            yaxis=dict(
                                title="Average Trip Duration (in minutes",
                                range=(0, 85)
                            )
                        )
                    }
                ),
                html.Div('''
                          The graph above shows the average duration of rides by day. As the seasons progress, the average trip distance stays relatively the same. However, we can see that the trip durations spike every weekend and drop during the weekdays. This is most likely because people use Bike Share as a quick way to commute to work on the weekdays, while on the weekends, people take the bikes as a slower, lesiure activity.
                            ''',
                         style={
                             'textAlign': 'center',
                         }
                         ),
            ])
        ]),
        dcc.Tab(label="Ridership over 24 Hours", children=[
            html.Div([
                dcc.Graph(
                      id="total-number-of-rides-by-time",
                      figure={
                          'data': [
                              go.Scatter(
                                  x=number_of_rides_by_time["Starting Time"],
                                  y=number_of_rides_by_time["count"],
                                  mode="lines",
                                  marker=dict(
                                      color='#9F5354'
                                  )
                              ),
                          ],
                          'layout': go.Layout(
                              title="Total Number of Rides by Time",
                              xaxis=dict(
                                  title="Time",
                              ),
                              yaxis=dict(
                                  title="Total Number of Rides"
                              )
                          )
                      }
                ),
                html.Div('''
                          This graph shows the total number of rides that started per minute. We see that the number of rides before 9 AM is relatively low, because nobody is out and about that early in the morning. At around 9 AM, there is a sudden spike as people head to work. We see similar spikes around lunch time (12PM -1PM), and around 5 PM when people head back home from work. Since the most popular starting station is Station 3069, bikes should be moved to Station 3069 and these peak activity times (around 9AM, 12-1PM, and around 5PM).
                          ''',
                         style={
                             'textAlign': 'center',
                             'marginTop': 25,
                             'marginRight': 25,
                             'marginLeft': 25,
                             'marginBottom': 25
                         }
                         ),

            ])
        ])
    ])
])

if __name__ == '__main__':
    app.run_server(debug=True)
