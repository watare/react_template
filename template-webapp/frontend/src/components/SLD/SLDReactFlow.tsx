/**
 * SLDReactFlow - Main ReactFlow component for Single Line Diagram
 *
 * Architecture:
 * - Uses ReactFlow for rendering and interaction
 * - Uses Dagre for automatic layout calculation
 * - Applies RTE rules (busbar horizontal, bay vertical)
 * - Custom nodes for equipment (with QElectroTech symbols)
 * - Drag-and-drop to adjust positions
 * - Save positions to RDF DiagramLayout
 */

import React, { useCallback, useEffect } from 'react';
import {
  ReactFlow,
  type Node,
  type Edge,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  type Connection,
  ConnectionMode,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';

import { EquipmentNode } from './nodes/EquipmentNode';
import { BusbarNode } from './nodes/BusbarNode';

// Custom node types
const nodeTypes = {
  equipment: EquipmentNode,
  busbar: BusbarNode,
};

interface SLDReactFlowProps {
  nodes: Node[];  // Already positioned by backend!
  edges: Edge[];
  onNodeDragStop?: (nodeId: string, position: { x: number; y: number }) => void;
}

export const SLDReactFlow: React.FC<SLDReactFlowProps> = ({
  nodes: initialNodes,
  edges: initialEdges,
  onNodeDragStop,
}) => {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  // Just set the nodes/edges received from backend (already positioned!)
  useEffect(() => {
    if (initialNodes.length > 0) {
      console.log('Received', initialNodes.length, 'nodes with positions from backend');
      console.log('First node position:', initialNodes[0]?.position);

      setNodes(initialNodes);
      setEdges(initialEdges);
    }
  }, [initialNodes, initialEdges, setNodes, setEdges]);

  // Handle node drag stop (save to backend)
  const handleNodeDragStop = useCallback(
    (_event: any, node: Node) => {
      if (onNodeDragStop) {
        onNodeDragStop(node.id, node.position);
      }
    },
    [onNodeDragStop]
  );

  // Handle connection (edge creation)
  const onConnect = useCallback(
    (connection: Connection) => {
      setEdges((eds) => addEdge(connection, eds));
    },
    [setEdges]
  );

  return (
    <div style={{ width: '100%', height: '100vh' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onNodeDragStop={handleNodeDragStop}
        nodeTypes={nodeTypes}
        connectionMode={ConnectionMode.Loose}
        fitView
        fitViewOptions={{ padding: 0.2 }}
        minZoom={0.1}
        maxZoom={2}
      >
        <Background />
        <Controls />
      </ReactFlow>
    </div>
  );
};
