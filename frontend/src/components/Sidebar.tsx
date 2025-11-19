import React, { useState } from 'react';
import { GoSidebarCollapse } from 'react-icons/go';
import { RiRobot2Line } from 'react-icons/ri';
import { AiOutlinePlus, AiOutlineMessage, AiOutlineDelete } from 'react-icons/ai';

interface Conversation {
  id: number;
  title: string;
  messages: { id: number; sender: 'user' | 'bot'; message: string }[];
  timestamp: string;
  category: 'today' | 'yesterday' | 'lastWeek';
}

interface SidebarProps {
  onNewContent?: () => void;
  conversations?: Conversation[];
}

const Sidebar: React.FC<SidebarProps> = ({ onNewContent, conversations = [] }) => {
  // Dummy conversation history
  const dummyConversations: Conversation[] = [
    {
      id: 1,
      title: 'Bar Chart Customization',
      messages: [
        { id: 1, sender: 'user', message: 'How do I customize bar chart colors?' },
        { id: 2, sender: 'bot', message: 'You can customize bar charts by adjusting the color palette in the chart settings.' }
      ],
      timestamp: '3:15 PM',
      category: 'today'
    },
    {
      id: 2,
      title: 'Real-time Dashboard Updates',
      messages: [
        { id: 1, sender: 'user', message: 'Can the dashboard update in real-time?' },
        { id: 2, sender: 'bot', message: 'Yes! The dashboard supports real-time data updates through WebSocket connections.' }
      ],
      timestamp: '1:42 PM',
      category: 'today'
    },
    {
      id: 3,
      title: 'Line Chart Data Formatting',
      messages: [
        { id: 1, sender: 'user', message: 'What format should my time series data be in?' },
        { id: 2, sender: 'bot', message: 'Time series data should include timestamp and value pairs for optimal visualization.' }
      ],
      timestamp: '10:30 AM',
      category: 'today'
    },
    {
      id: 4,
      title: 'Dashboard Responsive Design',
      messages: [
        { id: 1, sender: 'user', message: 'Is the dashboard mobile responsive?' },
        { id: 2, sender: 'bot', message: 'The dashboard is fully responsive and adapts to all screen sizes.' }
      ],
      timestamp: 'Yesterday',
      category: 'yesterday'
    },
    {
      id: 5,
      title: 'Pie Chart Legends',
      messages: [
        { id: 1, sender: 'user', message: 'How do I configure pie chart legends?' },
        { id: 2, sender: 'bot', message: 'Legends can be positioned and styled through the chart configuration options.' }
      ],
      timestamp: '2 days ago',
      category: 'lastWeek'
    },
    {
      id: 6,
      title: 'Dashboard Performance',
      messages: [
        { id: 1, sender: 'user', message: 'How many charts can I add to a dashboard?' },
        { id: 2, sender: 'bot', message: 'You can add multiple charts; performance depends on data volume and update frequency.' }
      ],
      timestamp: '4 days ago',
      category: 'lastWeek'
    },
    {
      id: 7,
      title: 'Heatmap Configuration',
      messages: [
        { id: 1, sender: 'user', message: 'How do I create a heatmap widget?' },
        { id: 2, sender: 'bot', message: 'Heatmaps can be created by providing a 2D data matrix with intensity values.' }
      ],
      timestamp: '5 days ago',
      category: 'lastWeek'
    }
  ];

  const [isCollapsed, setIsCollapsed] = useState<boolean>(false);
  const [activeConvo, setActiveConvo] = useState<number | null>(null);
  const [hoveredId, setHoveredId] = useState<number | null>(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState<number | null>(null);
  const [allConversations, setAllConversations] = useState<Conversation[]>(
    conversations.length > 0 ? conversations : dummyConversations
  );

  const groupedConversations = {
    today: allConversations.filter(c => c.category === 'today'),
    yesterday: allConversations.filter(c => c.category === 'yesterday'),
    lastWeek: allConversations.filter(c => c.category === 'lastWeek'),
  };

  const handleDeleteClick = (id: number, e: React.MouseEvent<HTMLButtonElement>) => {
    e.stopPropagation();
    setShowDeleteConfirm(id);
  };

  const confirmDelete = (id: number) => {
    setAllConversations(prev => prev.filter(c => c.id !== id));
    if (activeConvo === id) setActiveConvo(null);
    setShowDeleteConfirm(null);
  };

  const cancelDelete = () => {
    setShowDeleteConfirm(null);
  };

  const getConversationTitle = () => {
    const convo = allConversations.find(c => c.id === showDeleteConfirm);
    return convo?.title || 'this conversation';
  };

  return (
    <>
        {showDeleteConfirm !== null && (
          <div className="fixed inset-0 z-100 flex items-center justify-center bg-black/5 backdrop-blur-sm">
            <div className="bg-white rounded-xl shadow-2xl p-8 max-w-sm mx-4 animate-in fade-in zoom-in-95 duration-200">
              <h2 className="text-xl font-semibold text-gray-900 mb-2">Delete Conversation</h2>
              <p className="text-gray-600 mb-6">
                Are you sure you want to delete <span className="font-medium">"{getConversationTitle()}"</span>? This action cannot be undone.
              </p>
              <div className="flex gap-3 justify-end">
                <button
                  onClick={cancelDelete}
                  className="px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg font-medium transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={() => confirmDelete(showDeleteConfirm)}
                  className="px-4 py-2 text-white bg-red-600 hover:bg-red-700 rounded-lg font-medium transition-colors"
                >
                  Delete
                </button>
              </div>
            </div>
          </div>
        )}

        {isCollapsed && (
            <button
            onClick={() => setIsCollapsed(false)}
            className="fixed left-4 top-4 z-50 p-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg shadow-lg transition-all hover:scale-105"
            aria-label="Expand sidebar"
            >
            <GoSidebarCollapse className="w-5 h-5 rotate-180" />
            </button>
        )}
      
        <aside className={`h-screen ${isCollapsed ? 'w-0' : 'w-80'} shadow-xl flex flex-col border-l border-gray-200 bg-white transition-all duration-300 overflow-hidden z-50`}>
            {/* Header */}
            <header className="shrink-0 flex items-center justify-between p-5 border-b border-gray-100">
                <div className="flex items-center gap-3">
                <div className="p-2 bg-emerald-50 rounded-lg">
                    <RiRobot2Line className="w-6 h-6 text-emerald-600" />
                </div>
                <h4 className="text-xl font-semibold text-gray-900">NaveeBot</h4>
                </div>
                <button
                onClick={() => setIsCollapsed(!isCollapsed)}
                className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
                aria-label="Toggle sidebar"
                >
                <GoSidebarCollapse className="w-5 h-5" />
                </button>
            </header>

            {/* New Chat Button */}
            <div className="shrink-0 p-4 border-b border-gray-100">
                <button 
                  onClick={onNewContent}
                  className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg font-medium transition-colors shadow-sm hover:shadow"
                >
                <AiOutlinePlus className="w-5 h-5" />
                <span>New Content</span>
                </button>
            </div>

            {/* Conversations List */}
            <section className="flex-1 overflow-y-auto px-3 py-4">
                {/* Today */}
                {groupedConversations.today.length > 0 && (
                <div className="mb-6">
                    <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider px-3 mb-2">
                    Today
                    </p>
                    <div className="space-y-1">
                    {groupedConversations.today.map(convo => (
                        <div
                        key={convo.id}
                        onClick={() => setActiveConvo(convo.id)}
                        onMouseEnter={() => setHoveredId(convo.id)}
                        onMouseLeave={() => setHoveredId(null)}
                        className={`group relative flex items-center gap-3 px-3 py-2.5 rounded-lg cursor-pointer transition-all ${
                            activeConvo === convo.id
                            ? 'bg-emerald-50 text-emerald-900'
                            : 'hover:bg-gray-50 text-gray-700'
                        }`}
                        >
                        <AiOutlineMessage className={`w-4 h-4 shrink-0 ${
                            activeConvo === convo.id ? 'text-emerald-600' : 'text-gray-400'
                        }`} />
                        <div className="flex-1 min-w-0">
                            <p className="truncate text-sm font-medium">{convo.title}</p>
                            <p className="text-xs text-gray-500 mt-0.5">{convo.timestamp}</p>
                        </div>
                        {hoveredId === convo.id && (
                            <button
                            onClick={(e) => handleDeleteClick(convo.id, e)}
                            className="shrink-0 p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded transition-colors"
                            aria-label="Delete conversation"
                            >
                            <AiOutlineDelete className="w-4 h-4" />
                            </button>
                        )}
                        </div>
                    ))}
                    </div>
                </div>
                )}

                {/* Yesterday */}
                {groupedConversations.yesterday.length > 0 && (
                <div className="mb-6">
                    <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider px-3 mb-2">
                    Yesterday
                    </p>
                    <div className="space-y-1">
                    {groupedConversations.yesterday.map(convo => (
                        <div
                        key={convo.id}
                        onClick={() => setActiveConvo(convo.id)}
                        onMouseEnter={() => setHoveredId(convo.id)}
                        onMouseLeave={() => setHoveredId(null)}
                        className={`group relative flex items-center gap-3 px-3 py-2.5 rounded-lg cursor-pointer transition-all ${
                            activeConvo === convo.id
                            ? 'bg-emerald-50 text-emerald-900'
                            : 'hover:bg-gray-50 text-gray-700'
                        }`}
                        >
                        <AiOutlineMessage className={`w-4 h-4 shrink-0 ${
                            activeConvo === convo.id ? 'text-emerald-600' : 'text-gray-400'
                        }`} />
                        <div className="flex-1 min-w-0">
                            <p className="truncate text-sm font-medium">{convo.title}</p>
                            <p className="text-xs text-gray-500 mt-0.5">{convo.timestamp}</p>
                        </div>
                        {hoveredId === convo.id && (
                            <button
                            onClick={(e) => handleDeleteClick(convo.id, e)}
                            className="shrink-0 p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded transition-colors"
                            aria-label="Delete conversation"
                            >
                            <AiOutlineDelete className="w-4 h-4" />
                            </button>
                        )}
                        </div>
                    ))}
                    </div>
                </div>
                )}

                {/* Last 7 Days */}
                {groupedConversations.lastWeek.length > 0 && (
                <div className="mb-6">
                    <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider px-3 mb-2">
                    Last 7 Days
                    </p>
                    <div className="space-y-1">
                    {groupedConversations.lastWeek.map(convo => (
                        <div
                        key={convo.id}
                        onClick={() => setActiveConvo(convo.id)}
                        onMouseEnter={() => setHoveredId(convo.id)}
                        onMouseLeave={() => setHoveredId(null)}
                        className={`group relative flex items-center gap-3 px-3 py-2.5 rounded-lg cursor-pointer transition-all ${
                            activeConvo === convo.id
                            ? 'bg-emerald-50 text-emerald-900'
                            : 'hover:bg-gray-50 text-gray-700'
                        }`}
                        >
                        <AiOutlineMessage className={`w-4 h-4 shrink-0 ${
                            activeConvo === convo.id ? 'text-emerald-600' : 'text-gray-400'
                        }`} />
                        <div className="flex-1 min-w-0">
                            <p className="truncate text-sm font-medium">{convo.title}</p>
                            <p className="text-xs text-gray-500 mt-0.5">{convo.timestamp}</p>
                        </div>
                        {hoveredId === convo.id && (
                            <button
                            onClick={(e) => handleDeleteClick(convo.id, e)}
                            className="shrink-0 p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded transition-colors"
                            aria-label="Delete conversation"
                            >
                            <AiOutlineDelete className="w-4 h-4" />
                            </button>
                        )}
                        </div>
                    ))}
                    </div>
                </div>
                )}
            </section>
        </aside>
    </>
  );
};

export default Sidebar;