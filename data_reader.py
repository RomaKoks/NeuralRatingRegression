from torchtext import data
from constants import MAX_LENGTH
MIN_FREQ = 1

def amazon_dataset_iters(parent_path, device, batch_sizes=(32,256,256), verbose=True):
    """
        Arguments:
        parent_path: path to folder with train.json, val.json and test.json in Amazon format
        device: device to allocate barches on
        batch_sizes: tuple of (train_batch_size, val_batch_size, test_batch_size)
        verbose: True will print current status of processing
        Returns:
        (vocab, train_iter, val_iter, test_iter) - vocab and batch iterators for train, validation and test data.
        Each batch contains the following fields:
        batch.item - torch.LongTensor of shape (batch_size,) - numbers of reviewed items
        batch.user - torch.LongTensor of shape (batch_size,) - numbers of reviewers
        batch.text - torch.LongTensor of shape (word_num,batch_size) - encoded words in sentences
    """
    item = data.Field(sequential=False)
    user = data.Field(sequential=False)
    text = data.Field(sequential=True, 
                      tokenize='spacy',
                      init_token="$start",
                      eos_token="$end",
                      lower=True)
    tips = data.Field(sequential=True, 
                      tokenize='spacy',
                      init_token="$start",
                      eos_token="$end",
                      fix_length=MAX_LENGTH + 2,
                      lower=True)
    if verbose:
        print('Loading datasets...')
    train, val, test = data.TabularDataset.splits(
        path=parent_path,
        train='train.json',
        test='test.json',
        validation='val.json',
        format='json',
        fields={
            'asin':('item', item),
            'reviewerID':('user', user),
            'reviewText':('text', text),
            'summary':('tips', tips)
                }
    )
    if verbose:
        print('datasets loaded')
    item.build_vocab(train)
    if verbose:
        print('item vocab built')
    user.build_vocab(train)
    if verbose:
        print('user vocab built')
    text.build_vocab(train.text,train.tips, min_freq=MIN_FREQ)
    if verbose:
        print('text vocab built')
    tips.build_vocab(train.text,train.tips, min_freq=MIN_FREQ)
    if verbose:
        print('tips vocab built')
    train_iter, val_iter, test_iter = data.Iterator.splits(
        datasets=(train, val, test),
        batch_sizes=batch_sizes,
        device=device,
        repeat=False
    )
    return text.vocab, tips.vocab, train_iter, val_iter, test_iter