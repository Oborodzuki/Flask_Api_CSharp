using System.Net.Http.Json;
using System.Text;
using System.Text.Json;

namespace CSharpClient;

public class DataManagerUsingSystemTextJson : IDisposable
{
    private readonly string _baseUrl = "http://localhost:5001/api/data";
    private readonly HttpClient _httpClient;
    private readonly JsonSerializerOptions _jsonOptions;

    public DataManagerUsingSystemTextJson()
    {
        _httpClient = new HttpClient();
        _httpClient.Timeout = TimeSpan.FromSeconds(30);
        _jsonOptions = new JsonSerializerOptions
        {
            PropertyNameCaseInsensitive = true,
            PropertyNamingPolicy = JsonNamingPolicy.CamelCase
        };
    }

    public async Task<T> GetDataAsync<T>(string key, CancellationToken cancellationToken = default)
    {
        try
        {
            var response = await _httpClient.GetAsync($"{_baseUrl}/{key}", cancellationToken);
            response.EnsureSuccessStatusCode();

            var result = await response.Content.ReadFromJsonAsync<ApiResponse<T>>(_jsonOptions, cancellationToken);
            return result?.Success == true ? result.Data : default(T);
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error getting data: {ex.Message}");
            return default(T);
        }
    }

    public async Task<bool> SetDataAsync<T>(string key, T data, CancellationToken cancellationToken = default)
    {
        try
        {
            var response = await _httpClient.PostAsJsonAsync($"{_baseUrl}/{key}", data, _jsonOptions, cancellationToken);
            response.EnsureSuccessStatusCode();

            var result = await response.Content.ReadFromJsonAsync<ApiResponse>(_jsonOptions, cancellationToken);
            return result?.Success == true;
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error setting data: {ex.Message}");
            return false;
        }
    }

    public async Task<bool> DeleteDataAsync(string key, CancellationToken cancellationToken = default)
    {
        try
        {
            var response = await _httpClient.DeleteAsync($"{_baseUrl}/{key}", cancellationToken);
            response.EnsureSuccessStatusCode();

            var result = await response.Content.ReadFromJsonAsync<ApiResponse>(_jsonOptions, cancellationToken);
            return result?.Success == true;
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error deleting data: {ex.Message}");
            return false;
        }
    }

    public void Dispose()
    {
        _httpClient?.Dispose();
    }
}

public class ApiResponse
{
    public bool Success { get; set; }
    public string Error { get; set; }
}

public class ApiResponse<T> : ApiResponse
{
    public T Data { get; set; }
}