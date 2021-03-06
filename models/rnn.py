import torch
import torch.nn as nn
import torch.nn.functional as F


class Config(object):
    """https://www.itcodemonkey.com/article/9008.html"""
    # Data
    class_num = 2

    # Mode
    mode = 'LSTM'

    # Embedding
    pretrained_embedding = None  # pretrained_weight
    vocab_dim = 64
    vocab_size = 1024

    # RNN
    rnn_hidden_size = 128
    rnn_layers_num = 1
    bidirectional = True
    rnn_dropout = 0
    
    # Linear
    fc_dropout = 0


opt = Config()


class RNN(nn.Module):
    def __init__(self):
        super().__init__()
        # self.embed = nn.Embedding(V, D, max_norm=config.max_norm)
        self.embed = nn.Embedding(opt.vocab_size, opt.vocab_dim)
        if opt.pretrained_embedding:
            self.embed.weight.data.copy_(opt.pretrained_embedding)
            # self.embed.weight.requires_grad = False  # 冻结词向量

        self.rnn = nn.RNNBase(
            mode=opt.mode,
            input_size=opt.vocab_dim,
            hidden_size=opt.rnn_hidden_size,
            dropout=opt.rnn_dropout,
            num_layers=opt.rnn_layers_num,
            bidirectional=opt.bidirectional,
            batch_first=True  # input/output shape (batch, time_step, input_size)
        )
        __in_features = self.rnn.hidden_size * (self.rnn.bidirectional + 1)
        
        self.fc1 = nn.Linear(__in_features,
                             __in_features // 2)
        self.fc2 = nn.Linear(self.fc1.out_features, opt.class_num)

    def forward(self, x):
        assert isinstance(x, torch.LongTensor)
        x = self.embed(x)  # x/r_out shape (batch, time_step, input_size)
        r_out, (h_n, c_n) = self.rnn(x)  # h_n/c_n shape (num_layers * num_directions,  batch_size,  hidden_size)
        # r_out[:, -1, :].equal(h_n[-1, :, :])
        r_out = F.relu(r_out)
        x = self.fc1(r_out[:, -1, :])  # choose r_out at the last time step
        x = F.dropout(x, opt.fc_dropout, training=self.training) # __init__: self.dropout = nn.Dropout(opt.fc_dropout)
        y = self.fc2(x)
        # r_out = F.max_pool1d(r_out, r_out.size(2)).squeeze(2)
        # y = self.fc1(r_out)
        # y = self.fc2(y)
        return y
