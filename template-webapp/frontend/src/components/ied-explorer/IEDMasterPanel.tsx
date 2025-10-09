import React, { useState, useEffect } from 'react';

interface IED {
  uri: string;
  name: string;
  type: string;
  manufacturer: string;
  description?: string;
}

interface GroupedIEDs {
  [groupName: string]: IED[];
}

interface IEDMasterPanelProps {
  fileId: number;
  groupBy: 'type' | 'bay';
  searchQuery: string;
  selectedIED: string | null;
  onSelectIED: (ied: IED) => void;
}

export const IEDMasterPanel: React.FC<IEDMasterPanelProps> = ({
  fileId,
  groupBy,
  searchQuery,
  selectedIED,
  onSelectIED
}) => {
  const [groupedIEDs, setGroupedIEDs] = useState<GroupedIEDs>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [expandedGroups, setExpandedGroups] = useState<Set<string>>(new Set());

  useEffect(() => {
    fetchIEDs();
  }, [fileId, groupBy, searchQuery]);

  const fetchIEDs = async () => {
    setLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams({
        file_id: fileId.toString(),
        group_by: groupBy,
        search: searchQuery
      });

      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/api/ieds?${params}`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        }
      );

      if (!response.ok) {
        throw new Error('Failed to fetch IEDs');
      }

      const data = await response.json();
      setGroupedIEDs(data.groups || {});

      // Auto-expand all groups
      setExpandedGroups(new Set(Object.keys(data.groups || {})));

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  const toggleGroup = (groupName: string) => {
    const newExpanded = new Set(expandedGroups);
    if (newExpanded.has(groupName)) {
      newExpanded.delete(groupName);
    } else {
      newExpanded.add(groupName);
    }
    setExpandedGroups(newExpanded);
  };

  if (loading) {
    return <div className="ied-master-panel loading">Loading IEDs...</div>;
  }

  if (error) {
    return (
      <div className="ied-master-panel error">
        <p>Error: {error}</p>
        <button onClick={fetchIEDs}>Retry</button>
      </div>
    );
  }

  const groupNames = Object.keys(groupedIEDs).sort();

  return (
    <div className="ied-master-panel">
      <div className="ied-groups">
        {groupNames.length === 0 ? (
          <div className="empty-state">
            <p>No IEDs found</p>
          </div>
        ) : (
          groupNames.map(groupName => {
            const ieds = groupedIEDs[groupName];
            const isExpanded = expandedGroups.has(groupName);

            return (
              <div key={groupName} className="ied-group">
                <div
                  className="group-header"
                  onClick={() => toggleGroup(groupName)}
                >
                  <span className="group-icon">
                    {isExpanded ? '▼' : '▶'}
                  </span>
                  <span className="group-name">{groupName || 'Unknown'}</span>
                  <span className="group-count">({ieds.length})</span>
                </div>

                {isExpanded && (
                  <div className="group-items">
                    {ieds.map(ied => (
                      <div
                        key={ied.uri}
                        className={`ied-item ${selectedIED === ied.uri ? 'selected' : ''}`}
                        onClick={() => onSelectIED(ied)}
                      >
                        <div className="ied-name">{ied.name}</div>
                        {ied.manufacturer && (
                          <div className="ied-manufacturer">{ied.manufacturer}</div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
