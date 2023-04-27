from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import pandas as pd
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def assign_range(row, df):
    prev_prob = 0 if row.name == 0 else df.loc[row.name-1, 'cumulative_probability']
    start = int(round(prev_prob, 2)*100 ) + 1
    end = int(round(row['cumulative_probability'], 2) * 100)
    return f"{start:02d}-{end:02d}"


class Input(BaseModel):
    costomers: int
    inter_arrival_times: List[int]
    inter_arrival_probs: List[float]
    service_times: List[int]
    service_probs: List[float]
    random_arrival: List[int]
    random_service: List[int]


@app.get("/")
def root():
    return {"Hello World"}

@app.post("/createposts")
def create_post(data: Input):
    costomers = data.costomers
    inter_arrival_times = data.inter_arrival_times
    inter_arrival_probs = data.inter_arrival_probs
    service_times = data.service_times
    service_probs = data.service_probs
    random_arrival = data.random_arrival
    random_service = data.random_service
    
    head = ["Customer", "RN interval(t)","interval(t)","Arrival(t)","RN Service(t)","Service(t)"
        ,"Begin S(t)","Wait(t)","End S(t)","Sp(t)","ID(t)"]

    #construct table 1
    df_time = pd.DataFrame({
        'inter_arrival_time': inter_arrival_times,
        'probability': inter_arrival_probs
    })
    # Calculate the cumulative probability distribution
    df_time['cumulative_probability'] = df_time['probability'].cumsum()
    # Add the random digit assignment column
    df_time['random_digit_assignment'] = df_time.apply(assign_range, args=(df_time,), axis=1)

    #construct table 2
    df_service = pd.DataFrame({
        'service_time': service_times,
        'probability': service_probs
    })
    # Calculate the cumulative probability distribution
    df_service['cumulative_probability'] = df_service['probability'].cumsum()
    # Add the random digit assignment column
    df_service['random_digit_assignment'] = df_service.apply(assign_range, args=(df_service,), axis=1)

    table = []
    EndS = 0
    BeginS =0
    intervalValue = 0
    Arrival=0
    i = 1

    for row in range(int(costomers)):
        rowArray = []


        rowArray.append(int(row + 1))#Customer
        #RN_interval = int(input("Enter RN interval(t) for Customer "+str(row + 1)+": "))
        RN_interval = random_arrival[row]
        rowArray.append(RN_interval)#RN interval(t)
        #intervalValue = int(input("Enter interval(t) for Customer "+str(row + 1)+": "))
        match_row_time = df_time[df_time['random_digit_assignment'].apply(lambda x: int(x.split('-')[0]) <= int(RN_interval) <= int(x.split('-')[1]))]
        if len(match_row_time) == 0:
            intervalValue = 0
        else:
            intervalValue = match_row_time['inter_arrival_time'].iloc[0]
        rowArray.append(intervalValue)#interval(t)
        Arrival += intervalValue
        rowArray.append(Arrival)#Arrival(t)

        rowArray.append(random_service[row])#RN Service(t)
        match_row_service = df_service[df_service['random_digit_assignment'].apply(lambda x: int(x.split('-')[0]) <= int(round(random_service[row], 2)) <= int(x.split('-')[1]))]
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
    
    df = pd.DataFrame(table, columns=head)
    total_wait_time = df['Wait(t)'].sum()
    total_service_time = df['Service(t)'].sum()
    time_customer_spent_in_system = df['Sp(t)'].sum()
    print(df.to_json(orient='index'))

    return {"data": df.to_dict()}