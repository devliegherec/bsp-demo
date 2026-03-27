from __future__ import annotations
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

#count is a temporal solution to the following error 'There are multiple identical st.selectbox widgets with the same generated key.'
def stacked_barchart(df, x_column, stack_category, x_stack_column=None, key="key", unfiltered_df=None, Title = "", Binary = False, Time = True, Switch_view = True, Percentage=True, color_palette: "str | list" = 'blue', x_axis_order = None, stacking_order = None, height = 600, margin_top = None):

    if len(df)==0:
        return st.warning("⚠️ No patients to show")
    #initialization
    text_column = 'empty_column'
    col1,col2,col3,_,_= st.columns(5)

    #if no option to switch view is given (Switch_view = False), the default is a relative y axis
    if Switch_view:
        switch_view = col1.selectbox(
            'Y-axis view:',
            ['Relative values', 'Absolute values'],
            key = "y_view_"+key)
        
        detail = col1.checkbox(
            "display details", 
            key = "display_details_"+key)
        

        if switch_view == 'Relative values':
            y_column = 'proportion'
            hover_column = 'count'
            if detail:
                text_column = 'count'
        if switch_view == 'Absolute values':
            y_column = 'count'
            hover_column = 'proportion'
            if detail:
                text_column = 'proportion'
    else:
        if Percentage:
            y_column = 'proportion'
        else: 
            y_column = 'count'

        
    #Time = True meaning that the categories on the x axis are time related (a date)
    #in this case, we add the option to group the data per year, per quarter or per month
    if Time:
        #create time_interval dropdown with unique key
        time_interval = col2.selectbox(
            'X-axis time interval: ',
            ["Yearly","Quarterly","Monthly","Daily"],
            key="time_"+key,
            )
        df=convert_date(df,x_column,time_interval)
        if unfiltered_df is not None:
            unfiltered_df=convert_date(unfiltered_df,x_column,time_interval)
        x_column = 'date'
 
    #enforce order of categories on x_axis
    if x_axis_order != None:
        x_categories= x_axis_order
    else:
        x_categories = df.drop_duplicates(x_column, keep='first').sort_values(by=[x_column])[x_column]



    #enforce order of categories in bars
    if stacking_order != None:
        stack_groups = stacking_order
    else:
        stack_groups = df.drop_duplicates(stack_category, keep='first').sort_values(by=[stack_category])[stack_category]

    #preprocessing of dataframe
    df = order_df(df, x_column, x_categories)

    if x_stack_column is not None:

        #enforce order of categories on x_axis
        df = df.groupby([x_column,x_stack_column,stack_category]).size().reset_index(name='count')
        df['total'] = df.groupby([x_column,x_stack_column])['count'].transform('sum')
        df['proportion'] =  df['count'] / df['total']
        df_text = df.drop_duplicates(subset=[x_column,x_stack_column], keep='first')
        #df_text_x_stack = order_df(df_text_x_stack, x_stack_column, x_stack_categories)

    else: 
        df = df.groupby([x_column,stack_category]).size().reset_index(name='count')
        df['total'] = df.groupby([x_column])['count'].transform('sum')
        df['proportion'] =  df['count'] / df['total']
        df_text = df.drop_duplicates(subset=x_column, keep='first')
        df_text = order_df(df_text, x_column, x_categories)

    if unfiltered_df is not None:
        unfiltered_df = order_df(unfiltered_df, x_column, x_categories)
        unfiltered_df = unfiltered_df.groupby([x_column,stack_category]).size().reset_index(name='count_all')
        unfiltered_df['total_all'] = unfiltered_df.groupby([x_column])['count_all'].transform('sum')
        unfiltered_df['proportion_all'] =  unfiltered_df['count_all'] / unfiltered_df['total_all']
        unfiltered_df_text = unfiltered_df.drop_duplicates(subset=x_column, keep='first')
        unfiltered_df_text = order_df(unfiltered_df_text, x_column, x_categories)

    if Binary:
        df = df[df[stack_category]==True]
        stack_groups = [True]

    #position total absolute value on top of stacked barchart
    #if no option to switch view is given (Switch_view = False), the default is a relative y axis
    if len(df[y_column])>0:
        max_y_value = max(df[y_column])
        position_total = [-max_y_value/100]*len(df_text['total'])
        empty_chart=False
    else: 
        position_total=[0.05]*len(df_text['total'])
        empty_chart = True
        
        
    #if Switch_view and switch_view == 'Absolute values':
        #position_total = df_text['total']
    #    position_total = [-10]*len(df_text['total'])
   # else:
        #position_total = [1]*len(df_text['total'])
    #    position_total = [-0.01]*len(df_text['total'])


    #color palette for plot
    if color_palette == 'blue':
        color_list = ['#005fc4', '#008df6', '#67bdff', '#c0e2ff']
        color_text = '#005fc4'
    elif color_palette == 'red':
        color_list = ['#ca0025', '#ea625c', '#fea398', '#ffe4da']
        color_text = '#ca0025'
    elif color_palette == 'contrast':
        color_list = ["#49A7ED", "#FA9A34"]
        color_text = '#005fc4'
    elif color_palette == 'positive':
        color_list = ["#49A7ED", "#f5f2f2"]
        color_text = '#005fc4'
    elif color_palette == 'traffic_light':
        color_list = ["#73b504","#FFE800","#FA9A34","#ea625c",'#ca0025',"#d3d3d3"]
        color_text = '#005fc4'
    else:
        color_list=color_palette
        color_text='#000000'

    #figure
    fig = go.Figure()
    i = -1
    for group in stack_groups:
        i+=1
        i = i % len(color_list)
        #make a dataframe per stack (y-category)
        df_plot = df[df[stack_category]==group]
        df_plot = add_missing(df_plot,x_column,x_categories)

        if text_column == 'empty_column':
            df_plot['empty_column'] = ''
        if text_column == 'proportion':
            df_plot[text_column] = df_plot[text_column].apply(lambda x: '{0:1.0f}%'.format(100*x))
        
        if Binary:
            group = "" #we don't want the label 'True' to be displayed

        if x_stack_column is not None:
            x_trace = [df_plot[x_column],df_plot[x_stack_column]]
        else:
            x_trace = df_plot[x_column]
            
        #add trace to figure
        fig.add_trace(go.Bar(x=x_trace, 
                             y=df_plot[y_column], 
                             name=group,
                             marker=dict(color=color_list[i],opacity=0.65),
                             text = df_plot[text_column],
                             textposition='inside'
                             #hovertext= df_plot[hover_column]
                             ))

        if unfiltered_df is not None:
            #average for all hospitals
            fig.add_trace(go.Scatter(x=x_trace, 
                                y=1-unfiltered_df_text['proportion_all'],
                                text=1-unfiltered_df_text['proportion_all'],
                                mode='markers',
                                showlegend=False,
                                #hovertemplate = 'Average {text:str}: %{y:1.0f}%<extra></extra>',
                                #hovertemplate = 'Average text: %{y:$.2f}<extra></extra>',
                                hoverinfo='skip',
                                #hovertext= 1-df_text['proportion_all'],
                                marker_color='#000000'
                                ))
                        
        #total on top 
        fig.add_trace(go.Scatter(x=x_trace, 
                            y=position_total,
                            text=df_text['total'],
                            mode='text',
                            textposition='bottom center',
                            textfont=dict(size=12, color=color_text),
                            showlegend=False,
                            hoverinfo='skip'
                            ))

    fig.update_layout(title_text= Title)
    fig.update_layout(height=height,)
    if margin_top is not None:
        fig.update_layout(margin=dict(t=margin_top))
    fig.update_layout(plot_bgcolor='white')
    fig.update_layout(xaxis=dict(showgrid=True),yaxis=dict(showgrid=True))
    fig.update_yaxes(gridcolor='lightgrey')
    fig.update_layout(barmode='stack') # other option for barmode = 'group(ed)'
    fig.update_layout(legend=dict(orientation="h",yanchor="bottom", y=1.02, xanchor="right", x=1)) #legende boven plot
    fig.update_layout(xaxis={'categoryorder':'array', 'categoryarray':x_categories, 'type': 'category'})
    fig.update_layout(hovermode="x unified")
    fig.update_layout(uniformtext_minsize=12, uniformtext_mode='hide')
    if y_column == 'proportion':
        fig.update_layout(yaxis=dict(tickformat='.1%'))
    if empty_chart == True:
        fig.update_layout(yaxis=dict(range=[0,1]))
    st.plotly_chart(fig,use_container_width=True)
    return 



def add_missing(df,column,categories):
    for key in categories:
        if key not in list(df[column]):
                df = pd.concat([df, pd.DataFrame([pd.Series(0, index=df.columns)])], ignore_index=True)
                df[column] = df[column].replace([0],key)
    df = order_df(df, column, categories)
    return df


def order_df(df, column, order_list):
    df[column] = df[column].astype("category")
    df[column] = df[column].cat.set_categories(order_list)
    df.sort_values(column) 
    return df

def convert_date(df,x_column,time_interval):
    
    df[x_column] = pd.to_datetime(df[x_column])

    if time_interval == "Yearly":
        df['date'] = df[x_column].dt.to_period('Y')
    elif time_interval == "Quarterly":
        df['date'] = df[x_column].dt.to_period('Q')
    elif time_interval == "Monthly":
        df['date'] = df[x_column].dt.to_period('M')
    elif time_interval == "Daily":
        df['date'] = df[x_column].dt.to_period('D')
    df['date'] = df['date'].astype(str)
    return df
