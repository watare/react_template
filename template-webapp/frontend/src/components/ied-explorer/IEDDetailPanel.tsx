import React, { useState, useEffect } from 'react';
import { ExpandableTree, TreeNode } from '../common/ExpandableTree';

interface IED {
  uri: string;
  name: string;
  type: string;
  manufacturer: string;
  description?: string;
}

interface IEDDetailPanelProps {
  fileId: number;
  selectedIED: IED | null;
}

export const IEDDetailPanel: React.FC<IEDDetailPanelProps> = ({ fileId, selectedIED }) => {
  const [treeRoot, setTreeRoot] = useState<TreeNode | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (selectedIED) {
      loadIEDTree();
    } else {
      setTreeRoot(null);
    }
  }, [selectedIED]);

  const loadIEDTree = () => {
    if (!selectedIED) return;

    // Create root node
    const root: TreeNode = {
      uri: selectedIED.uri,
      name: selectedIED.name,
      type: 'IED',
      hasChildren: true,
      isExpanded: false,
      children: null,
      manufacturer: selectedIED.manufacturer,
      iedType: selectedIED.type
    };

    setTreeRoot(root);
  };

  const handleExpand = async (node: TreeNode) => {
    // If already loaded, just toggle
    if (node.children !== null) {
      node.isExpanded = !node.isExpanded;
      // Force a new tree object to trigger re-render
      setTreeRoot(treeRoot ? { ...treeRoot } : null);
      return;
    }

    // Fetch children
    setLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams({
        file_id: fileId.toString(),
        parent_uri: encodeURIComponent(node.uri),
        parent_type: node.type
      });

      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/api/ieds/tree?${params}`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        }
      );

      if (!response.ok) {
        throw new Error('Failed to fetch tree children');
      }

      const data = await response.json();

      console.log('Fetched children for', node.name, ':', data.children.length, 'children');
      console.log('Children data:', data.children);

      // Convert API response to TreeNode format
      const children = data.children.map((child: any) => ({
        uri: child.uri,
        name: child.name,
        type: child.type,
        hasChildren: child.hasChildren,
        isExpanded: false,
        children: null,
        ...child  // Include all metadata
      }));

      // Update node
      node.children = children;
      node.isExpanded = true;

      console.log('Node after expansion:', node);
      console.log('Num children:', children.length);

      // Force re-render with a fresh copy
      setTreeRoot({ ...treeRoot! });

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      console.error('Error fetching tree children:', err);
    } finally {
      setLoading(false);
    }
  };

  if (!selectedIED) {
    return (
      <div className="ied-detail-panel empty">
        <div className="empty-state">
          <h3>No IED Selected</h3>
          <p>Select an IED from the left panel to view its details</p>
        </div>
      </div>
    );
  }

  return (
    <div className="ied-detail-panel">
      <div className="ied-header">
        <h2>{selectedIED.name}</h2>
        <div className="ied-metadata">
          <div className="metadata-item">
            <span className="label">Type:</span>
            <span className="value">{selectedIED.type}</span>
          </div>
          <div className="metadata-item">
            <span className="label">Manufacturer:</span>
            <span className="value">{selectedIED.manufacturer}</span>
          </div>
          {selectedIED.description && (
            <div className="metadata-item">
              <span className="label">Description:</span>
              <span className="value">{selectedIED.description}</span>
            </div>
          )}
        </div>
      </div>

      <div className="ied-tree-container">
        <h3>IED Hierarchy</h3>
        {error && (
          <div className="error-message">
            <p>Error: {error}</p>
          </div>
        )}
        <ExpandableTree
          rootNode={treeRoot}
          onExpand={handleExpand}
          loading={loading}
        />
      </div>
    </div>
  );
};
