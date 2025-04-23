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


export default function Home() {
  const [water, setWater] = useState(0)
  const isFetching = useRef(false);

  useEffect(() => {
    const fetchMostRecent = async () => {
      // prevent race conditions
      if (isFetching.current) return;
      isFetching.current = true

      try {
        const response = await fetch(
          'https://19af-2607-f140-400-60-c4ca-302e-2368-53d7.ngrok-free.app/get_most_recent',
          {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ bottle_name: 'bottle_1' }),
          }
        );

        const data = await response.json();
        console.log('Response:', data);

        setWater(data)
      } catch (error) {
        console.error('Error fetching most recent:', error);
      }

      isFetching.current = false

    };

    const intervalId = setInterval(fetchMostRecent, 200);

    // Clean up on unmount
    return () => clearInterval(intervalId);

  }, []);

  return (
    <div className="text-center">
      <div className="h-[60px]"></div>
      <div className="font-bold font-xl">
        water bottle program
      </div>
      <WaterLevel level={water}/>
    </div>
  );
}
