"use client"
import Image from "next/image";
import { useEffect, useState, useRef } from "react";

function WaterLevel({ level }) {
  const clampedLevel = Math.max(0, Math.min(100, level));

  return (
    <div className="flex flex-col items-center">
      <div className="relative h-64 w-16 border-4 border-blue-500 rounded-2xl overflow-hidden">
        <div
          className="absolute bottom-0 left-0 w-full bg-blue-400 transition-all duration-500"
          style={{ height: `${clampedLevel}%` }}
        />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 text-black font-bold">
          {clampedLevel}%
        </div>
      </div>
      <p className="mt-2 text-sm font-bold text-gray-700">Water Level</p>
    </div>
  );
}

const BACKEND_DOMAIN = "https://09c8-2607-f140-400-60-59e2-cb12-e25-4b2c.ngrok-free.app"


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

  return (
    <div className="text-center">
      <div className="h-[60px]"></div>
      <div className="font-bold font-xl">
        water bottle program
      </div>

      <div className="flex justify-center">
        {bottles.map((bottle_name, bottle_i) => (
          <div className="m-10" key={bottle_i}>
            <div>{bottle_name}</div>

            <div>{pickups[bottle_name].length} pickups today</div>

            {pickups[bottle_name].map((dp, dp_i) => (
              <div key={dp_i}>
                {dp["duration"]}s - {dp["time"]}
              </div>
            ))}
            
          </div>
        ))}
      </div>

    </div>
  );
}
