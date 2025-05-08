"use client"
import Image from "next/image";
import { useEffect, useState, useRef } from "react";


const dehydration_limit = 10; // the amount of time without drinking to be considered dehydrated


function secondsPast(timeStr) {
  // Get current time in PST as a Date object
  const now = new Date(new Date().toLocaleString("en-US", { timeZone: "America/Los_Angeles" }));

  // Get today's date in PST in MM/DD/YYYY format
  const pstDateStr = new Intl.DateTimeFormat('en-US', {
    timeZone: 'America/Los_Angeles',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  }).format(now);

  // Combine date with input time string
  const fullDateTimeStr = `${pstDateStr} ${timeStr}`;

  // Create a Date object for the input time (still interpreted as local, so adjust)
  const inputTime = new Date(new Date(fullDateTimeStr).toLocaleString('en-US', {
    timeZone: 'America/Los_Angeles'
  }));

  // Calculate the difference in seconds
  const diffInSeconds = Math.floor((now - inputTime) / 1000);

  return diffInSeconds;
}



function round_tenth(number) {
  return Math.round(number * 10) / 10;
}

const BACKEND_DOMAIN = "https://me100-final-project-1.onrender.com/"

export default function Home() {
  const [pickups, setPickups] = useState({})
  const isFetching = useRef(false);

  useEffect(() => {
    const fetchMostRecent = async () => {
      // prevent race conditions
      if (isFetching.current) return;
      isFetching.current = true

      try {
        const response = await fetch(
          `${BACKEND_DOMAIN}/get_database`, {
            headers: new Headers({
              "ngrok-skip-browser-warning": "69420",
            }),
          }
        );

        let data = await response.json()

        setPickups(data)

      } catch (error) {
        console.error('Error fetching most recent:', error);
      }

      isFetching.current = false

    };

    const intervalId = setInterval(fetchMostRecent, 200);

    // Clean up on unmount
    return () => clearInterval(intervalId);

  }, []);


  const bottles = Object.keys(pickups)

  const pickups_data = []

  for (let bottle_name of bottles) {
    const new_bottle = {}
    const raw_data = pickups[bottle_name]

    new_bottle.name = bottle_name
    new_bottle.time_drank = round_tenth(pickups[bottle_name].reduce((sum, item) => sum + (item.duration || 0), 0))
    new_bottle.num_pickups = pickups[bottle_name].length
    new_bottle.data = pickups[bottle_name]

    if (raw_data.length > 0) {
      new_bottle.second_since_drink = secondsPast(raw_data[raw_data.length - 1]?.time)
    }
    else {
      new_bottle.second_since_drink = 100
    }

    pickups_data.push(new_bottle)
  }

  const maxTimeDrank = round_tenth(Math.max(...pickups_data.map(drink => drink.time_drank)));

  console.log(maxTimeDrank)

  return (
    <div className="text-center">
      <div className="h-[60px]"></div>
      <div className="font-bold text-3xl">
        Are my friends hydrated?
      </div>

      <div className="flex justify-center">
        {pickups_data.map((data, i) => (
          <div className="m-10" key={i}>
            <div>
              {data.time_drank == maxTimeDrank ? (
                <div>
                  <img className="m-auto" src="crown.png" height={50} width={50}/> 
                </div>
              ):(
                <div className="h-[35px]"></div>
              )}
            </div>
            <div className="font-bold text-2xl">
              {data.name}
            </div>
            <div className="font-bold">
              {data.second_since_drink < dehydration_limit ? "HYDRATED" : "DEHYDRATED"}
            </div>
            {data.second_since_drink < dehydration_limit ? (
              <div>
                <img src="strong_spongebob.webp" height={200}/>
              </div>
            ) : (
              <div>
                <img src="dehydrated_spongebob.jpg" height={200}/>
              </div>
            )}
            <div>
              --- stats ---

            </div>

            <div>
              {data.num_pickups} pickups today
            </div>
            <div>
              {data.time_drank}s drank today
            </div>
            <div>
              last drank water at {data.data.length ? data.data[data.data.length - 1].time : "N/A"}
            </div>
            <div>
              seconds since last drink {data.second_since_drink}
            </div>

            <div>
              --- data ---
            </div>

            {
              data.data.map((v, i) => (
                <div key={i}>
                  {v.duration}s @ {v.time}
                </div>
              ))
            }
          </div>

        ))}
      </div>

    </div>
  );
}
