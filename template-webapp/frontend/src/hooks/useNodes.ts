import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { nodesApi } from '../services/api'

export function useNodes() {
  return useQuery({
    queryKey: ['nodes'],
    queryFn: nodesApi.list,
  })
}

export function useNode(id: string) {
  return useQuery({
    queryKey: ['node', id],
    queryFn: () => nodesApi.get(id),
    enabled: !!id,
  })
}

export function useCreateNode() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: nodesApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['nodes'] })
    },
  })
}

export function useUpdateNode() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, properties }: { id: string; properties: Record<string, string> }) =>
      nodesApi.update(id, properties),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['node', id] })
      queryClient.invalidateQueries({ queryKey: ['nodes'] })
    },
  })
}

export function useDeleteNode() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: nodesApi.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['nodes'] })
    },
  })
}

export function useSearchNodes(query: string) {
  return useQuery({
    queryKey: ['nodes', 'search', query],
    queryFn: () => nodesApi.search(query),
    enabled: query.length >= 3,
  })
}

export function useNodeStats() {
  return useQuery({
    queryKey: ['nodes', 'stats'],
    queryFn: nodesApi.stats,
  })
}
