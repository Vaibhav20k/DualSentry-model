package errors

type RetryableError struct {
	Err error
}

func (e *RetryableError) Error() string {
	return e.Err.Error()
}

func NewRetryable(err error) error {
	return &RetryableError{
		Err: err,
	}
}

func IsRetryable(err error) bool {
	_, ok := err.(*RetryableError)
	return ok
}
