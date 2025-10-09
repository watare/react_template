import React, { useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { IEDMasterPanel } from '../components/ied-explorer/IEDMasterPanel';
import { IEDDetailPanel } from '../components/ied-explorer/IEDDetailPanel';
import './IEDExplorerPage.css';

interface IED {
  uri: string;
  name: string;
  type: string;
  manufacturer: string;
  description?: string;
}

export default function IEDExplorerPage() {
  const [searchParams] = useSearchParams();
  const fileId = searchParams.get('file_id');

  const [groupBy, setGroupBy] = useState<'type' | 'bay'>('type');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedIED, setSelectedIED] = useState<IED | null>(null);

  if (!fileId) {
    return (
      <div className="ied-explorer-page error">
        <h1>IED Explorer</h1>
        <p>Error: No file ID provided</p>
      </div>
    );
  }

  const handleSelectIED = (ied: IED) => {
    setSelectedIED(ied);
  };

  return (
    <div className="ied-explorer-page">
      <div className="page-header">
        <h1>IED Explorer</h1>
        <p className="subtitle">Navigate IEC 61850 Intelligent Electronic Devices</p>
      </div>

      <div className="explorer-controls">
        <div className="control-group">
          <label>Group By:</label>
          <div className="radio-group">
            <label className="radio-label">
              <input
                type="radio"
                value="type"
                checked={groupBy === 'type'}
                onChange={(e) => setGroupBy(e.target.value as 'type')}
              />
              IED Type
            </label>
            <label className="radio-label">
              <input
                type="radio"
                value="bay"
                checked={groupBy === 'bay'}
                onChange={(e) => setGroupBy(e.target.value as 'bay')}
              />
              Bay Name
            </label>
          </div>
        </div>

        <div className="control-group search-group">
          <label htmlFor="search">Search:</label>
          <input
            id="search"
            type="text"
            placeholder="Filter IEDs..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="search-input"
          />
        </div>
      </div>

      <div className="explorer-container">
        <div className="master-panel-container">
          <IEDMasterPanel
            fileId={parseInt(fileId)}
            groupBy={groupBy}
            searchQuery={searchQuery}
            selectedIED={selectedIED?.uri || null}
            onSelectIED={handleSelectIED}
          />
        </div>

        <div className="detail-panel-container">
          <IEDDetailPanel
            fileId={parseInt(fileId)}
            selectedIED={selectedIED}
          />
        </div>
      </div>
    </div>
  );
}
