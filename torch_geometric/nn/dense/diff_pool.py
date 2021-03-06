import torch


class DenseDiffPool(torch.nn.Module):
    r"""Differentiable Pooling Operator based on dense learned assignments
    :math:`S` with

    .. math::
        \begin{align}
        F^{(l+1)} &= S^{(l)} X^{(l)}\\
        A^{(l+1)} &= {S^{(l)}}^{\top}A^{(l)} S^{(l)}
        \end{align}

    from the `"Hierarchical Graph Representation Learning with Differentiable
    Pooling" <https://arxiv.org/abs/1806.08804>`_ paper.

    Args:
        gnn_pool (torch.nn.Module): An instance of a GNN module to compute soft
            assignments.
    """

    def __init__(self, gnn_pool):
        super(DenseDiffPool, self).__init__()

        self.gnn_pool = gnn_pool

    def reset_parameters(self):
        self.gnn_pool.reset_parameters()

    def forward(self, x, adj):
        s = self.gnn_pool(x, adj)
        s = torch.softmax(s, dim=-1)

        x = x.unsqueeze(0) if x.dim() == 2 else x
        adj = adj.unsqueeze(0) if adj.dim() == 2 else adj
        s = s.unsqueeze(0) if s.dim() == 2 else s

        out = torch.matmul(s.transpose(1, 2), x)
        out_adj = torch.matmul(torch.matmul(s.transpose(1, 2), adj), s)

        reg = adj - torch.matmul(s, s.transpose(1, 2))
        reg = torch.norm(reg, p=2)
        reg = reg / reg.numel()

        return out, out_adj, reg

    def __repr__(self):
        return '{}({}, {})'.format(self.__class__.__name__,
                                   self.gnn_pool.in_channels,
                                   self.gnn_pool.out_channels)
