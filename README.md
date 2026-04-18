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

Data Architecture:
  The CSV version of the dataset was acquired from Capital Bikeshare. To guarantee correctness and consistency, the data is first extracted and cleansed using an ETL procedure. Following processing, the information is kept in a data warehouse that facilitates effective querying and analysis. 

The structure is: Data Source → ETL Procedure → Data Storage → Dashboard

Dimensional Modeling:
  One fact table and several dimension tables make up the star schema used in the construction of the data warehouse.
          trip_id (Primary Key)
          start_station_id and end_station_id (Foreign keys)
          user_id (Foreign Key)
          trip_duration date_id (Foreign Key)
          Dim of the Station: station_name location station_id (Primary Key)
          User_Dim: user_type user_id (Primary Key)
          Date_Dim: date_id (Primary Key) day, month, and year

Deliverables:

  Capital Bikeshare dataset is the data source.
  Data explanation: The dataset includes trip-level data, such as stations, start and end times, and user details.
  A separate Excel or Google Sheets file contains the data dictionary.
  GitHub repository: Established and kept up to date for this project
  Fact and dimension tables are included in the data model.
  Data warehouse: Designed to handle and store massive amounts of bike ride information

  
                                                
