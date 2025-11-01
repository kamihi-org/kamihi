"""
Base question class.

License:
    MIT

"""

from collections.abc import Callable, Coroutine
from typing import Any

from telegram import Update
from telegram.ext import CallbackContext, MessageHandler, filters

from kamihi.tg import send


class Question:
    """Base class for questions."""

    question_text: str
    error_text: str

    _param_name: str

    def with_param_name(self, param_name: str) -> "Question":
        """
        Set the parameter name for the question.

        Args:
            param_name (str): The name of the parameter.

        Returns:
            Question: The question instance with the parameter name set.

        """
        self._param_name = param_name
        return self

    async def ask_question(self, update: Update, context: CallbackContext) -> None:
        """
        Send the question text to the user.

        Args:
            update (Update): The update object.
            context (CallbackContext): The callback context.

        """
        await send(self.question_text, update, context)

    @property
    def filters(self) -> filters.BaseFilter:
        """
        Return the filters for the answer to the question.

        Override this method to customize the filters used to capture the user's response.

        Returns:
            filters.BaseFilter: The filters for the answer to the question.

        """
        return filters.TEXT & ~filters.COMMAND

    def handler(self, func: Callable[[Update, CallbackContext], Coroutine[Any, Any, Any]]) -> MessageHandler:
        """
        Return the handler for the answer to the question.

        Do not override this method. Instead, override the `filters` property to customize the filters used.

        Args:
            func (Callable): The function to handle the user's response.

        Returns:
            MessageHandler: The handler for the answer to the question.

        """
        return MessageHandler(self.filters, func)

    async def get_response(self, update: Update, context: CallbackContext) -> Any:  # skipcq: PYL-R0201
        """
        Get the response from the user.

        Override this method to customize how the response is retrieved from the update and/or context.

        Args:
            update (Update): The update object.
            context (CallbackContext): The callback context.

        Returns:
            Any: The response from the user, which can be of any type.

        """
        return update.message.text

    async def validate_before(  # skipcq: PYL-R0201
        self,
        response: Any,
        update: Update | None = None,
        context: CallbackContext | None = None,
    ) -> Any:
        """
        Validate the user's response before Kamihi's built-in validation.

        Override this method to add validation before Kamihi's built-in validation. Raising a ValueError indicates an invalid
        response, and the error message will be sent to the user.

        Args:
            response (Any): The response from the user.
            update (Update, optional): The update object. Defaults to None.
            context (CallbackContext, optional): The callback context. Defaults to None.

        Returns:
            Any: The further validated response, which can be of any type.

        Raises:
            ValueError: If the response is invalid.

        """
        return response

    async def _validate_internal(  # skipcq: PYL-R0201
        self,
        response: Any,
        update: Update | None = None,
        context: CallbackContext | None = None,
    ) -> Any:
        """
        Validate the user's response using Kamihi's built-in validation.

        Override this method to implement Kamihi's built-in validation logic.

        Args:
            response (Any): The response from the user.
            update (Update, optional): The update object. Defaults to None.
            context (CallbackContext, optional): The callback context. Defaults to None.

        Returns:
            Any: The validated response, which can be of any type.

        Raises:
            ValueError: If the response is invalid.

        """
        return response

    async def validate_after(  # skipcq: PYL-R0201
        self,
        response: Any,
        update: Update | None = None,
        context: CallbackContext | None = None,
    ) -> Any:
        """
        Validate the user's response after Kamihi's built-in validation.

        Override this method to add validation after Kamihi's built-in validation. Raising a ValueError indicates an invalid
        response, and the error message will be sent to the user.

        Args:
            response (Any): The response from the user.
            update (Update, optional): The update object. Defaults to None.
            context (CallbackContext, optional): The callback context. Defaults to None.

        Returns:
            Any: The further validated response, which can be of any type.

        Raises:
            ValueError: If the response is invalid.

        """
        return response

    async def validate(
        self,
        response: Any,
        update: Update | None = None,
        context: CallbackContext | None = None,
    ) -> Any:
        """
        Validate the user's response.

        This method is what unifies the validation process. It first calls `validate_before`, then performs any built-in
        validation (if applicable), and finally calls `validate_after`. Only override this method if you want to
        completely replace the validation process.

        Args:
            response (Any): The response from the user.
            update (Update, optional): The update object. Defaults to None.
            context (CallbackContext, optional): The callback context. Defaults to None.

        Returns:
            Any: The validated response, which can be of any type.

        Raises:
            ValueError: If the response is invalid.

        """
        response = await self.validate_before(response, update, context)
        response = await self._validate_internal(response, update, context)
        return await self.validate_after(response, update, context)

    async def _save(self, response: Any, context: CallbackContext) -> None:
        """
        Save the response from the user.

        Args:
            response (Any): The response from the user.
            context (CallbackContext): The callback context.

        """
        context.chat_data["questions"][self._param_name] = response

    def entry(
        self,
        current_state: int,
        prev_exit: Callable[[Update, CallbackContext], Coroutine[Any, Any, bool]] | None = None,
    ) -> Callable[[Update, CallbackContext], Coroutine[Any, Any, int]]:
        """
        Return the entry function for the question.

        Args:
            current_state (int): The current state of the conversation.
            prev_exit (Callable, optional): The exit function of the last question. Defaults to None.

        Returns:
            Callable: The entry function for the question.

        """

        async def _enter(update: Update, context: CallbackContext) -> int:
            """Entry function for the question."""
            if prev_exit:
                prev_exited_successfully = await prev_exit(update, context)
                if not prev_exited_successfully:
                    return current_state

            await self.ask_question(update, context)
            return current_state + 1

        return _enter

    def exit(self) -> Callable[[Update, CallbackContext], Coroutine[Any, Any, bool]]:
        """
        Return the exit function for the question.

        Returns:
            Callable: The exit function for the question.

        """

        async def _exit(update: Update, context: CallbackContext) -> bool:
            """Exit function for the question."""
            res = await self.get_response(update, context)

            try:
                res = await self.validate(res, update, context)
            except ValueError as e:
                await send(str(e), update, context)
                return False

            await self._save(res, context)
            return True

        return _exit
