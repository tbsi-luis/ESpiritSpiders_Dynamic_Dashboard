import React, { useState } from 'react'
import type { DashboardResponse } from '../services/apiClient'
import { CanvasDashboard, ChatbotBoard } from '../components'

const DynamicDashboard: React.FC = () => {
  const [dashboardData, setDashboardData] = useState<DashboardResponse | null>(null)

  const handleDashboardGenerated = (data: DashboardResponse) => {
    setDashboardData(data)
  }

  return (
    <div className='w-full h-screen flex flex-row items-end p-10 gap-15'>
      <CanvasDashboard dashboardData={dashboardData} />
      <ChatbotBoard onDashboardGenerated={handleDashboardGenerated} />
    </div>
  )
}

export default DynamicDashboard