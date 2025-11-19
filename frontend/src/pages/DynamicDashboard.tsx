import React, { useState } from 'react'
import type { DashboardResponse } from '../services/apiClient'
import { CanvasDashboard, ChatbotBoard, Sidebar } from '../components'

const DynamicDashboard: React.FC = () => {
  const [dashboardData, setDashboardData] = useState<DashboardResponse | null>(null)

  const handleDashboardGenerated = (data: DashboardResponse) => {
    setDashboardData(data)
  }

  return (
    <div className='w-full h-screen flex flex-row'>
      <Sidebar />
      <ChatbotBoard onDashboardGenerated={handleDashboardGenerated} />
      <CanvasDashboard dashboardData={dashboardData} />
    </div>
  )
}

export default DynamicDashboard