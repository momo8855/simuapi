import streamlit as st
import pandas as pd

def assign_range(row, df):
    prev_prob = 0 if row.name == 0 else df.loc[row.name-1, 'cumu_prob']
    start = int(round(prev_prob, 2)*100 ) + 1
    end = int(round(row['cumu_prob'], 2) * 100)
    return f"{start:02d}-{end:02d}"

def simulate_queue(customers, inter_arrival_times, inter_arrival_probs, service_times, service_probs, random_arrival, random_service):
    df_time = pd.DataFrame({
    'arrival_time': inter_arrival_times,
    'prob': inter_arrival_probs
    })

    # Calculate the cumulative probability distribution
    df_time['cumu_prob'] = df_time['prob'].cumsum()

    # Add the random digit assignment column
    df_time['random_ranges'] = df_time.apply(assign_range, args=(df_time,), axis=1)



    #construct table 2
    df_service = pd.DataFrame({
        'service_time': service_times,
        'prob': service_probs
    })

    # Calculate the cumulative probability distribution
    df_service['cumu_prob'] = df_service['prob'].cumsum()

    # Add the random digit assignment column
    df_service['random_ranges'] = df_service.apply(assign_range, args=(df_service,), axis=1)

    table = []
    EndS = 0
    BeginS =0
    intervalValue = 0
    Arrival=0
    i = 1

    for row in range(int(customers)):
        rowArray = []


        rowArray.append(int(row + 1))#Customer
        #RN_interval = int(input("Enter RN interval(t) for Customer "+str(row + 1)+": "))
        RN_interval = random_arrival[row] if row != 0 else ' '
        rowArray.append(RN_interval)#RN interval(t)
        #intervalValue = int(input("Enter interval(t) for Customer "+str(row + 1)+": "))
        match_row_time = df_time[df_time['random_ranges'].apply(lambda x: int(x.split('-')[0]) <= int(RN_interval) <= int(x.split('-')[1]))] if row != 0 else None
        
        intervalValue = 0 if row == 0 else match_row_time['arrival_time'].iloc[0]

            
        rowArray.append(intervalValue)#interval(t)
        Arrival += intervalValue
        rowArray.append(Arrival)#Arrival(t)

        rowArray.append(random_service[row])#RN Service(t)
        match_row_service = df_service[df_service['random_ranges'].apply(lambda x: int(x.split('-')[0]) <= int(round(random_service[row], 2)) <= int(x.split('-')[1]))]
        service = match_row_service['service_time'].iloc[0]
        #service = int(input("Enter Service(t) for Customer "+str(row+1)+": "))
        rowArray.append(service)#Service

        if ((row > 0) and (EndS > Arrival)) :
            BeginS = EndS 
        else:
            BeginS = Arrival 

        if((row == 5*i) and (EndS > Arrival)) :
            BeginS = EndS + 10  
            i += 1
        elif((row == 5*i) and (EndS < Arrival)) :
            BeginS = Arrival + 10 
            i += 1 

        IDe = BeginS- EndS  if (row > 0) else 0
        rowArray.append(BeginS )#Begin S(t)
        Wait = BeginS - Arrival if BeginS > Arrival else 0
        rowArray.append(Wait)#Wait(t)
        EndS = BeginS + service
        rowArray.append(EndS)#End S(t)
        Spend = Wait + service
        rowArray.append(Spend)#Sp(t)
        rowArray.append(IDe)#ID(t)
        table.append(rowArray)

    head = ["Customer", "RNA","interval(t)","Arrival(t)","RNS","Service(t)"
        ,"Begin S(t)","Wait(t)","End S(t)","Sp(t)","ID(t)"]
    df_simulation = pd.DataFrame(table, columns=head)

    return  df_simulation ,df_time, df_service

st.write("""
# Simple  Queue Simulation App
Shown are the **Simulation Table** and ***Chart*** of Analysis!
""")
input0 = st.text_input('Enter number of customers')

# Create two columns
col1, col2 = st.columns(2)

# Input boxes for column 1
with col1:
    st.header('Inter Arrival')
    input1 = st.text_input('times', key='input1')
    input2 = st.text_input('probs', key='input2')
    input3 = st.text_input('randoms', key='input3')

# Input boxes for column 2
with col2:
    st.header('Service Time')
    input4 = st.text_input('times', key='input4')
    input5 = st.text_input('probs', key='input5')
    input6 = st.text_input('randoms', key='input6')

valid_inputs = True

    # Split the inputs by spaces and convert to lists of numbers
try:
    costomers = int(input0)
    inter_arrival_times = [int(num) for num in input1.split(', ')]
    inter_arrival_probs = [float(num) for num in input2.split(', ')]
    random_arrival = [int(num) for num in input3.split(', ')]
    random_arrival.insert(0, 0)
    service_times = [int(num) for num in input4.split(', ')]
    service_probs = [float(num) for num in input5.split(', ')]
    random_service = [int(num) for num in input6.split(', ')]
except ValueError:
    valid_inputs = False

# Convert inputs to lists of numbers on button click
if st.button('Simulate'):
    if valid_inputs:
        df_1, df_2, df_3 = simulate_queue(customers = costomers, inter_arrival_times = inter_arrival_times, inter_arrival_probs = inter_arrival_probs, 
                                      service_times = service_times, service_probs = service_probs, random_arrival = random_arrival, random_service = random_service)
        # Use streamlit_columns to create two columns
        col1, col2 = st.columns(2)

        df_2 = df_2.set_index('arrival_time')
        df_3 = df_3.set_index('service_time')

        # Display the dataframes in each column
        with col1:
            st.write('Table 1')
            st.write(df_2)

        with col2:
            st.write('Table 2')
            st.write(df_3)


        df_1 = df_1.set_index('Customer')
        st.write('Simulation Table')
        st.write(df_1)

        chart_data = df_1['Wait(t)']
        st.write('Simulation Chart')
        st.bar_chart(chart_data)

    if not valid_inputs:
        st.error('Invalid input. Please enter only numbers separated by commas and spaces.')