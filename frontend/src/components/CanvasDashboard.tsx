import React, { useEffect, useRef } from 'react'
import { RiRobot2Line } from "react-icons/ri";
import type { DashboardResponse } from '../services/apiClient'

interface CanvasDashboardProps {
  dashboardData?: DashboardResponse | null;
}

const CanvasDashboard: React.FC<CanvasDashboardProps> = ({ dashboardData }) => {
  const htmlContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (htmlContainerRef.current && dashboardData?.html) {
      console.log("🎨 Rendering HTML content to canvas");
      console.log("HTML length:", dashboardData.html.length);
      
      try {
        // Clear previous content
        htmlContainerRef.current.innerHTML = '';
        
        // Create a container for the content
        const container = document.createElement('div');
        container.className = 'w-full';
        
        // Set the HTML content
        container.innerHTML = dashboardData.html;
        
        // Append to ref
        htmlContainerRef.current.appendChild(container);
        
        console.log("✅ HTML content rendered successfully");
        
        // Re-trigger any scripts in the HTML
        const scripts = container.querySelectorAll('script');
        if (scripts.length > 0) {
          console.log(`📜 Found ${scripts.length} script(s) to execute`);
          
          scripts.forEach((script, index) => {
            try {
              // Wait a bit to ensure external libraries are loaded
              setTimeout(() => {
                const newScript = document.createElement('script');
                newScript.textContent = script.textContent;
                newScript.async = true;
                document.body.appendChild(newScript);
                console.log(`✅ Script ${index + 1} executed`);
              }, 100 * (index + 1));
            } catch (error) {
              console.error(`❌ Error executing script ${index + 1}:`, error);
            }
          });
        }
        
      } catch (error) {
        console.error("❌ Error rendering HTML:", error);
      }
    } else {
      if (!dashboardData?.html) {
        console.log("⏳ Waiting for HTML content...");
      }
    }
  }, [dashboardData?.html]);

  return (
    <div className='h-full w-full flex flex-col border border-gray-300 rounded-lg'>
        <header className='w-full h-fit p-4 bg-white shadow-md flex flex-row items-center justify-between'>
            <p className='font-semibold text-xl'>Navee Board</p>
            <button className='bg-emerald-500 rounded-md px-3 py-2 font-semibold text-white'>Download</button>
        </header>
        <main className='w-full h-full overflow-y-auto flex flex-col gap-6 p-6'>
            {!dashboardData?.html ? (
              <div className='w-full h-full flex items-center justify-center'>
                <div className='w-fit h-fit flex flex-col items-center'>
                    <RiRobot2Line className='w-20 h-20 text-gray-400 mb-4'/>
                    <p className='text-gray-500'>Ask NaveeBot anything you want...</p>
                </div>
              </div>
            ) : (
                <div ref={htmlContainerRef} className='w-full' />
            )}
        </main>
    </div>
  )
}

export default CanvasDashboard