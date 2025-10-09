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

interface Hierarchy {
  [substationName: string]: {
    [voltageLevelName: string]: {
      [bayName: string]: IED[];
    };
  };
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
  const [hierarchy, setHierarchy] = useState<Hierarchy>({});
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

      if (groupBy === 'bay') {
        // Hierarchical structure
        setHierarchy(data.hierarchy || {});

        // Auto-expand all levels
        const allKeys = new Set<string>();
        Object.keys(data.hierarchy || {}).forEach(substation => {
          allKeys.add(substation);
          Object.keys(data.hierarchy[substation] || {}).forEach(voltageLevel => {
            allKeys.add(`${substation}/${voltageLevel}`);
            Object.keys(data.hierarchy[substation][voltageLevel] || {}).forEach(bay => {
              allKeys.add(`${substation}/${voltageLevel}/${bay}`);
            });
          });
        });
        setExpandedGroups(allKeys);
      } else {
        // Simple grouping
        setGroupedIEDs(data.groups || {});
        setExpandedGroups(new Set(Object.keys(data.groups || {})));
      }

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

  // Render hierarchical view (bay grouping)
  if (groupBy === 'bay') {
    const substationNames = Object.keys(hierarchy).sort();

    if (substationNames.length === 0) {
      return (
        <div className="ied-master-panel">
          <div className="empty-state">
            <p>No IEDs found</p>
          </div>
        </div>
      );
    }

    return (
      <div className="ied-master-panel">
        <div className="ied-groups">
          {substationNames.map(substationName => {
            const voltageLevels = hierarchy[substationName];
            const voltageLevelNames = Object.keys(voltageLevels).sort();
            const isSubstationExpanded = expandedGroups.has(substationName);

            return (
              <div key={substationName} className="ied-group hierarchy-level-1">
                {/* Substation Level */}
                <div
                  className="group-header substation-header"
                  onClick={() => toggleGroup(substationName)}
                >
                  <span className="group-icon">
                    {isSubstationExpanded ? '▼' : '▶'}
                  </span>
                  <span className="group-name">{substationName}</span>
                </div>

                {isSubstationExpanded && voltageLevelNames.map(voltageLevelName => {
                  const bays = voltageLevels[voltageLevelName];
                  const bayNames = Object.keys(bays).sort();
                  const vlKey = `${substationName}/${voltageLevelName}`;
                  const isVLExpanded = expandedGroups.has(vlKey);

                  return (
                    <div key={vlKey} className="ied-group hierarchy-level-2">
                      {/* VoltageLevel */}
                      <div
                        className="group-header voltage-level-header"
                        onClick={() => toggleGroup(vlKey)}
                      >
                        <span className="group-icon">
                          {isVLExpanded ? '▼' : '▶'}
                        </span>
                        <span className="group-name">{voltageLevelName}</span>
                      </div>

                      {isVLExpanded && bayNames.map(bayName => {
                        const ieds = bays[bayName];
                        const bayKey = `${vlKey}/${bayName}`;
                        const isBayExpanded = expandedGroups.has(bayKey);

                        return (
                          <div key={bayKey} className="ied-group hierarchy-level-3">
                            {/* Bay */}
                            <div
                              className="group-header bay-header"
                              onClick={() => toggleGroup(bayKey)}
                            >
                              <span className="group-icon">
                                {isBayExpanded ? '▼' : '▶'}
                              </span>
                              <span className="group-name">{bayName}</span>
                              <span className="group-count">({ieds.length})</span>
                            </div>

                            {isBayExpanded && (
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
                      })}
                    </div>
                  );
                })}
              </div>
            );
          })}
        </div>
      </div>
    );
  }

  // Render simple grouped view (type grouping)
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
