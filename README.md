# Capital-Bikeshare
This projects end goal is to analyze Capital Bikeshare data to improve their operational efficiency and user experience

Business Requirments:
  Identify andanalyze when bike usage is at it's highestb whether it is day time or night time
  Identify which stations are the most popular or in demand
  Analyze on how to improve bike availability and station popularity

Functional Requirments:
  What my system is going to is the following:
      Allow users to view bike usage and when they are least/most available
      Track trips between stations 
      Calculate how long a avrage trip is 
      Locate the most practical and in demand stations
      Store and retrieve historical data

Data Requirements:
  I retried this data from open portal through csv export. It contains thr following information {trip_id, start_time, end_time, start_station, end_station, bike_id, user_type,
                                                                          gender, birth_year, trip_duration}
  Easily reaching about 1 million rows and 15+ columns

Information Architecture:
  This system enables users to engage with bike share data. The dashboard interface allows users to see trends over time, travel data, and station usage. The system has two primary user    roles: The dataset can be updated and managed by admin users. Reports and trends can be viewed by general users. The system receives data from the source dataset, processes it, and       stores it. Users can then access the processed data through reports and visualizations.

