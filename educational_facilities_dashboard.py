#import libraries
import streamlit as st
import pandas as pd
import plotly.express as px


#set config page
st.set_page_config(
    page_title="Educational Facilities in Nigeria Dashboard",
    page_icon="📖",
    layout="wide"
 )

@st.cache_data
def load_data():
    try:
        df = pd.read_csv("data/Cleaned_educational_facilities_in_nigeria.csv")
        return df
    except FileNotFoundError as e:
        st.warning(f"An error occured: {e}")




def create_sidebar_filters(df):
    st.sidebar.header("Interactive Filters")

    Facility_Display_Type = st.sidebar.multiselect(
        "Select Facility_Type_Display",
        options=df['Facility_Display_Type'].unique(),
        default=df['Facility_Display_Type'].unique()
    )

    Management = st.sidebar.multiselect(
        "Select Management(s)",
        options=df['Management'].unique(),
        default=df['Management'].unique()
    )

    Unique_LGA = st.sidebar.multiselect(
        "Select Unique_LGA(s)",
        options=df['Unique_LGA'].unique(),
        default=df['Unique_LGA'].unique()
    )


    return Facility_Display_Type, Management, Unique_LGA

def filter_data(df, Facility_Display_Type, Management, Unique_LGA):
    filtered_df = df[df['Facility_Display_Type'].isin(Facility_Display_Type) & df['Management'].isin(Management) & df['Unique_LGA'].isin(Unique_LGA)]
    return filtered_df

def display_metrics(filtered_df):
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("🏨 Total Num Schools", f"{len(filtered_df):,.2f}")

    with col2:
        st.metric("👨‍👩‍👧‍👦 Total Num Students", f"{len(filtered_df):,.2f}")

    with col3:
        avg_students = filtered_df['Total_Students_Number'].mean() if len(filtered_df) > 0 else 0
        st.metric("🤷‍♂️ Average Students", f"{avg_students:,.2f}")

    with col4:
        electricity_perctg = (filtered_df['PHCN_Electricity'] == True).sum() / len(filtered_df) * 100 if len(filtered_df) > 0 else 0
        st.metric("💡 PHCN Electricity", f"{electricity_perctg:,.1f}%")

    with col5:
        water_supply_pct = (filtered_df['Improved_Water_Supply'] == True).sum() / len(filtered_df) * 100 if len(filtered_df) > 0 else 0
        st.metric("💧Improved Water Supply", f"{water_supply_pct:.1f}%")

def display_charts(filtered_df):
    if len(filtered_df) == 0:
        st.warning("No filter data to display. Please adjust the data from the sidebar")
        return
    col1, col2 = st.columns(2)

    
    #st.subheader("DISTRIBUTION OF SCHOOL TYPES")
    facility_type = filtered_df['Facility_Display_Type'].value_counts()
    fig1 = px.bar(
        x=facility_type.values,
        y=facility_type.index,
        title="DISTRIBUTION OF SCHOOL TYPES"
    )
    fig1.update_layout(xaxis_title=" School Count", yaxis_title="School Type")
    st.plotly_chart(fig1, width='stretch')
    

    fig2 = px.histogram(
    filtered_df, x='Total_Students_Number', nbins=50,
          title="STUDENT POPULATION DISTRIBUTION"
    )
    fig2.update_traces(marker_line_color='white',marker_line_width=1)
    st.plotly_chart(fig2, width='stretch')

    with col1:
        comparison = (filtered_df.groupby('Management')[['Total_Students_Number', 'Total_Teachers']].mean().reset_index())   
        fig3= px.bar(
            comparison,
            x='Management',
            y=['Total_Students_Number', 'Total_Teachers'],
            barmode='group',
            title='PUBLIC VS PRIVATE SCHOOL: AVERAGE STUDENTS AND TEACHERS',
            labels={
                'Management': 'School Management',
                'value': 'Average Count',
                'variable': 'Metric'
            }
        )
        st.plotly_chart(fig3, width='stretch')


    with col2:
        water_supply_pct = (
        filtered_df['Improved_Water_Supply'].mean() * 100
        )
        sanitation_perctg = (filtered_df['Improved_Sanitation'].mean() * 100)

        access = pd.DataFrame({
            'Category':['Water','Sanitation'],
            'Percentage':[water_supply_pct,sanitation_perctg]
    
        })
        fig4 = px.pie(
            access,
            values='Percentage',
            names='Category',
            title='WATER AND SANITATION ACCESS'
        )
        st.plotly_chart(fig4, width='stretch')

    col3, col4 = st.columns(2)
    with col3:
        electricity_perctg = filtered_df['PHCN_Electricity'].value_counts().reset_index()
        electricity_perctg.columns = ['Electricity', 'Count']

        fig5 = px.pie(
        electricity_perctg,
        names='Electricity',
        values='Count',
        title='ELECTRICITY AVAILABILITY IN SCHOOLS'
        )
        st.plotly_chart(fig5, width='stretch')

    with col4:
        fig6 = px.scatter_mapbox(filtered_df,
            lat='Latitude',
            lon='Longitude',
            hover_name='Facility_Name',
            zoom=4,
            height=600
        )
        fig6.update_layout(
            mapbox_style='open-street-map'
        )
        st.plotly_chart(fig6, width='stretch')

def display_table_data(filtered_df):
    if len (filtered_df) > 0:
        st.dataframe(filtered_df, width='stretch', height=300)
    else:
        st.warning("No Educational data to display")




def main():
    #load dataset
    df = load_data()

    #sidebar
    Facility_Display_Type, Management, Unique_LGA =  create_sidebar_filters(df)

    #filtered_data
    filtered_df = filter_data(df, Facility_Display_Type, Management, Unique_LGA)

    st.title("Educational Facilities in Nigeria Dashboard")
    st.markdown("---")

    #display metrics
    display_metrics(filtered_df)

    # display chart
    display_charts(filtered_df)

    # display table_data
    display_table_data(filtered_df)


main()


