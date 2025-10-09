import React from 'react';

export interface TreeNode {
  uri: string;
  name: string;
  type: string;
  hasChildren: boolean;
  isExpanded?: boolean;
  children?: TreeNode[] | null;
  [key: string]: any; // Additional metadata
}

interface ExpandableTreeProps {
  node: TreeNode;
  onExpand: (node: TreeNode) => void;
  level?: number;
}

const TreeNodeComponent: React.FC<ExpandableTreeProps> = ({ node, onExpand, level = 0 }) => {
  const handleToggle = () => {
    if (node.hasChildren) {
      onExpand(node);
    }
  };

  const getIcon = () => {
    if (!node.hasChildren) {
      return <span className="tree-icon">•</span>;
    }
    return (
      <span className="tree-icon clickable">
        {node.isExpanded ? '▼' : '▶'}
      </span>
    );
  };

  const getNodeLabel = () => {
    return (
      <span className="tree-label">
        <span className="tree-name">{node.name}</span>
        {node.type && (
          <span className="tree-type"> [{node.type}]</span>
        )}
      </span>
    );
  };

  return (
    <div className="tree-node">
      <div
        className="tree-node-content"
        style={{ paddingLeft: `${level * 20}px` }}
        onClick={handleToggle}
      >
        {getIcon()}
        {getNodeLabel()}
      </div>

      {node.isExpanded && node.children && (
        <div className="tree-children">
          {node.children.map((child, index) => (
            <TreeNodeComponent
              key={child.uri || index}
              node={child}
              onExpand={onExpand}
              level={level + 1}
            />
          ))}
        </div>
      )}

      {node.isExpanded && node.children && node.children.length === 0 && (
        <div
          className="tree-empty"
          style={{ paddingLeft: `${(level + 1) * 20}px` }}
        >
          <span className="text-muted">No children</span>
        </div>
      )}
    </div>
  );
};

interface ExpandableTreeRootProps {
  rootNode: TreeNode | null;
  onExpand: (node: TreeNode) => void;
  loading?: boolean;
}

export const ExpandableTree: React.FC<ExpandableTreeRootProps> = ({
  rootNode,
  onExpand,
  loading = false
}) => {
  if (loading) {
    return <div className="tree-loading">Loading tree...</div>;
  }

  if (!rootNode) {
    return <div className="tree-empty">No data to display</div>;
  }

  return (
    <div className="expandable-tree">
      <TreeNodeComponent node={rootNode} onExpand={onExpand} />
    </div>
  );
};
